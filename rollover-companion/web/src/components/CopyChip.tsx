"use client";

import { useState } from "react";

export function CopyChip({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      className="flex w-full items-start justify-between gap-3 rounded-card border border-bee-border bg-cream px-4 py-3 text-left transition-colors hover:border-bee-blue/40 hover:bg-bee-blue-light/30"
    >
      <div className="min-w-0 flex-1">
        <p className="text-xs font-bold uppercase tracking-wide text-bee-muted">{label}</p>
        <p className="mt-1 break-words text-sm font-medium text-bee-ink lg:text-base">{value}</p>
      </div>
      <span className="shrink-0 text-xs font-semibold text-bee-blue">
        {copied ? "Copied!" : "Copy"}
      </span>
    </button>
  );
}
