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
      className="relative overflow-hidden rounded-2xl border-2 border-[#FFC72C]/55 bg-gradient-to-br from-[#FFF9E6] via-white to-[#FFF4D6] p-8 shadow-[0_6px_28px_rgba(255,199,44,0.16)] sm:p-10"
      role="region"
      aria-label="Check payable-to security instruction"
    >
      <div className="mb-6 flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#111111] text-lg text-white"
            aria-hidden
          >
            🔒
          </span>
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-[#9A6200]">
              Critical — check payable to
            </p>
            <p className="mt-1 text-sm leading-relaxed text-[#555555]">
              Use this exact wording or your rollover may be rejected.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={copy}
          className="pb-interactive shrink-0 rounded-xl bg-[#111111] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#1E242B]"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <p className="text-2xl font-bold leading-tight tracking-tight text-[#1E242B] sm:text-3xl">
        {payableLine}
      </p>
    </div>
  );
}
