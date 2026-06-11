import { NextRequest, NextResponse } from "next/server";
import { handleDemoRequest, isDemoBackendEnabled } from "@/lib/demoEngine";

const TIMEOUT_MS = 10_000;

function apiBase(): string {
  return (process.env.API_URL || "").replace(/\/$/, "");
}

async function proxyToLiveApi(req: NextRequest, pathSegments: string[]) {
  const path = pathSegments.join("/");
  const target = `${apiBase()}/api/${path}${req.nextUrl.search}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const headers = new Headers();
    const contentType = req.headers.get("content-type");
    if (contentType) headers.set("content-type", contentType);

    const init: RequestInit = {
      method: req.method,
      headers,
      signal: controller.signal,
    };
    if (req.method !== "GET" && req.method !== "HEAD") {
      init.body = await req.text();
    }

    const upstream = await fetch(target, init);
    const body = await upstream.text();

    return new NextResponse(body, {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") || "application/json",
      },
    });
  } catch {
    return NextResponse.json(
      {
        detail:
          "Could not reach the rollover API. Confirm your API host is running and CORS_ORIGINS includes this site.",
        code: "API_UNREACHABLE",
        configured: true,
      },
      { status: 503 }
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

async function handleRequest(req: NextRequest, pathSegments: string[]) {
  const bodyText =
    req.method !== "GET" && req.method !== "HEAD" ? await req.text() : "";

  if (isDemoBackendEnabled()) {
    return handleDemoRequest(req.method, pathSegments, bodyText, req.nextUrl.search);
  }

  return proxyToLiveApi(req, pathSegments);
}

type RouteContext = { params: { path: string[] } };

export async function GET(req: NextRequest, ctx: RouteContext) {
  return handleRequest(req, ctx.params.path);
}

export async function POST(req: NextRequest, ctx: RouteContext) {
  return handleRequest(req, ctx.params.path);
}

export async function PUT(req: NextRequest, ctx: RouteContext) {
  return handleRequest(req, ctx.params.path);
}

export async function PATCH(req: NextRequest, ctx: RouteContext) {
  return handleRequest(req, ctx.params.path);
}

export async function DELETE(req: NextRequest, ctx: RouteContext) {
  return handleRequest(req, ctx.params.path);
}
