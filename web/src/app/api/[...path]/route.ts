import { NextRequest, NextResponse } from "next/server";

const TIMEOUT_MS = 10_000;

function apiBase(): string {
  return (process.env.API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
}

function apiConfigured(): boolean {
  return Boolean(process.env.API_URL?.trim());
}

async function proxy(req: NextRequest, pathSegments: string[]) {
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
        detail: apiConfigured()
          ? "Could not reach the rollover API. Confirm Railway is running and CORS_ORIGINS includes this Vercel URL."
          : "API_URL is not set on Vercel. Deploy rollover-companion on Railway, add API_URL to Environment Variables, then redeploy.",
        code: "API_UNREACHABLE",
        configured: apiConfigured(),
      },
      { status: 503 }
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

type RouteContext = { params: { path: string[] } };

export async function GET(req: NextRequest, ctx: RouteContext) {
  return proxy(req, ctx.params.path);
}

export async function POST(req: NextRequest, ctx: RouteContext) {
  return proxy(req, ctx.params.path);
}

export async function PUT(req: NextRequest, ctx: RouteContext) {
  return proxy(req, ctx.params.path);
}

export async function PATCH(req: NextRequest, ctx: RouteContext) {
  return proxy(req, ctx.params.path);
}

export async function DELETE(req: NextRequest, ctx: RouteContext) {
  return proxy(req, ctx.params.path);
}
