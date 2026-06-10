"use client";

import { useState } from "react";

export function FinancialCopyField({
  label,
  value,
  compact = false,
}: {
  label: string;
  value: string;
  compact?: boolean;
}) {
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
    <div
      className={`flex items-stretch gap-0 overflow-hidden rounded-xl border border-[#EAE5DC] bg-white shadow-sm ${
        compact ? "" : ""
      }`}
    >
      <div className="min-w-0 flex-1 px-4 py-3.5">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          {label}
        </p>
        <p className="mt-1 break-words text-base font-semibold leading-snug text-[#111111]">
          {value}
        </p>
      </div>
      <button
        type="button"
        onClick={copy}
        className="shrink-0 border-l border-[#EAE5DC] bg-[#FAF8F5] px-4 text-sm font-semibold text-[#111111] transition-colors hover:bg-[#FFF4D6] active:scale-[0.98]"
        aria-label={`Copy ${label}`}
      >
        {copied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
}
