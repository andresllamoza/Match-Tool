import { NextResponse } from "next/server";
import {
  demoAction,
  demoFunnel,
  demoGet,
  demoHealth,
  demoProviders,
  demoStart,
} from "./handlers";
import { isDemoJourneyId } from "./state";

export async function handleDemoRequest(
  method: string,
  pathSegments: string[],
  bodyText: string,
  search: string
): Promise<NextResponse> {
  const path = pathSegments.join("/");

  if (path === "health" && method === "GET") {
    return NextResponse.json(demoHealth());
  }

  if (path === "providers" && method === "GET") {
    return NextResponse.json(demoProviders());
  }

  if (path === "funnel" && method === "GET") {
    return NextResponse.json(demoFunnel());
  }

  if (path === "journey/start" && method === "POST") {
    const agent = search.includes("agent=true");
    const res = demoStart();
    if (agent) {
      return NextResponse.json({ ...res, provider_intel: { demo: true } });
    }
    return NextResponse.json(res);
  }

  const journeyMatch = path.match(/^journey\/([^/]+)(?:\/action)?$/);
  if (journeyMatch) {
    const journeyId = decodeURIComponent(journeyMatch[1]);
    if (!isDemoJourneyId(journeyId)) {
      return NextResponse.json({ detail: "Journey not found" }, { status: 404 });
    }

    if (path.endsWith("/action") && method === "POST") {
      const body = bodyText ? (JSON.parse(bodyText) as Record<string, unknown>) : {};
      const agent = search.includes("agent=true");
      const result = demoAction(journeyId, body);
      if (!result) {
        return NextResponse.json({ detail: "Journey not found" }, { status: 404 });
      }
      if ("assistant" in result) {
        const snapshot = demoGet(journeyId);
        if (!snapshot) {
          return NextResponse.json({ detail: "Journey not found" }, { status: 404 });
        }
        return NextResponse.json({ ...snapshot, assistant: result.assistant });
      }
      if (agent) {
        return NextResponse.json({ ...result, provider_intel: { demo: true } });
      }
      return NextResponse.json(result);
    }

    if (method === "GET") {
      const res = demoGet(journeyId);
      if (!res) {
        return NextResponse.json({ detail: "Journey not found" }, { status: 404 });
      }
      return NextResponse.json(res);
    }
  }

  return NextResponse.json({ detail: "Not found" }, { status: 404 });
}
