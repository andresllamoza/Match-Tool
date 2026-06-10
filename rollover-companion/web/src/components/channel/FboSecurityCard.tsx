"use client";

import { useState } from "react";
import { isFboPayableLine } from "@/lib/checkPayable";

export function FboSecurityCard({ payableLine }: { payableLine: string }) {
  const [copied, setCopied] = useState(false);

  if (!payableLine || !isFboPayableLine(payableLine)) return null;

  async function copy() {
    try {
      await navigator.clipboard.writeText(payableLine);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  }

  return (
    <div
      className="relative overflow-hidden rounded-2xl border-2 border-[#FFC72C]/60 bg-gradient-to-br from-[#FFF9E6] via-white to-[#FFF4D6] p-5 shadow-[0_4px_24px_rgba(255,199,44,0.18)] lg:p-6"
      role="region"
      aria-label="Check payable-to security instruction"
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#111111] text-base text-white"
            aria-hidden
          >
            🔒
          </span>
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-[#9A6200]">
              Critical — check payable to
            </p>
            <p className="text-sm text-[#555555]">
              Use this exact wording or your rollover may be rejected.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={copy}
          className="shrink-0 rounded-lg bg-[#111111] px-3.5 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#1E242B] active:scale-[0.98]"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <p className="text-2xl font-bold leading-tight tracking-tight text-[#111111] lg:text-3xl">
        {payableLine}
      </p>
    </div>
  );
}
