"use client";

import Link from "next/link";
import { Button } from "./ui/Button";

function resolveMessage(raw: string | null): { title: string; body: string; isSetup: boolean } {
  const lower = (raw || "").toLowerCase();

  if (
    lower.includes("api_url is not set") ||
    lower.includes("api_unreachable") ||
    lower.includes("[api_unreachable]")
  ) {
    return {
      title: "Rollover engine not connected",
      body: "The customer app is live, but it needs a Railway API behind it. This takes about 10 minutes to wire up.",
      isSetup: true,
    };
  }

  if (lower.includes("cors") || lower.includes("railway")) {
    return {
      title: "Can't reach the rollover API",
      body: raw || "Confirm Railway is running and CORS_ORIGINS includes this site's URL.",
      isSetup: true,
    };
  }

  return {
    title: "We're having trouble reaching our servers",
    body: "Check your connection and try again. If this keeps happening, a BeeKeeper can help.",
    isSetup: false,
  };
}

export function ApiBootstrapError({
  error,
  loading,
  onRetry,
}: {
  error: string | null;
  loading?: boolean;
  onRetry?: () => void;
}) {
  const { title, body, isSetup } = resolveMessage(error);

  return (
    <div className="mx-auto w-full max-w-lg text-left">
      <span className="mb-3 block text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
        Rollover Companion
      </span>
      <h1 className="mb-6 text-3xl font-extrabold leading-[1.1] tracking-[-0.03em] text-bee-charcoal sm:text-4xl">
        Let&apos;s find your old 401(k)
      </h1>

      <div
        className="mb-6 rounded-block border border-bee-yellow/40 bg-bee-yellow-tint px-5 py-4"
        role="alert"
      >
        <p className="font-bold text-bee-charcoal">{title}</p>
        <p className="mt-2 text-sm leading-relaxed text-bee-ink">{body}</p>
      </div>

      {isSetup && (
        <ol className="mb-8 space-y-3 text-sm leading-relaxed text-bee-ink">
          <li className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bee-charcoal text-xs font-bold text-white">
              1
            </span>
            <span>
              <strong className="text-bee-charcoal">Railway</strong> — deploy from GitHub with root
              directory <code className="rounded bg-white px-1.5 py-0.5 text-xs">rollover-companion</code>
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bee-charcoal text-xs font-bold text-white">
              2
            </span>
            <span>
              <strong className="text-bee-charcoal">Vercel</strong> — set{" "}
              <code className="rounded bg-white px-1.5 py-0.5 text-xs">API_URL</code> to your Railway
              URL, then redeploy
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bee-charcoal text-xs font-bold text-white">
              3
            </span>
            <span>
              <strong className="text-bee-charcoal">Railway env</strong> —{" "}
              <code className="rounded bg-white px-1.5 py-0.5 text-xs">CORS_ORIGINS</code> = your
              Vercel URL
            </span>
          </li>
        </ol>
      )}

      <div className="space-y-3">
        {onRetry && (
          <Button onClick={onRetry} disabled={loading}>
            {loading ? "Connecting…" : "Try again"}
          </Button>
        )}
        <Link
          href="/"
          className="pb-text-link text-bee-muted hover:text-bee-charcoal"
        >
          ← Back to home
        </Link>
      </div>
    </div>
  );
}
