"use client";

import { useState } from "react";

export function FinancialCopyField({
  label,
  value,
}: {
  label: string;
  value: string;
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
    <div className="flex items-stretch overflow-hidden rounded-2xl border border-[#EAE5DC] bg-white shadow-sm">
      <div className="min-w-0 flex-1 px-5 py-4 sm:px-6 sm:py-5">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          {label}
        </p>
        <p className="mt-2 break-words text-base font-semibold leading-snug text-[#1E242B] sm:text-lg">
          {value}
        </p>
      </div>
      <button
        type="button"
        onClick={copy}
        className="pb-interactive shrink-0 border-l border-[#EAE5DC] bg-[#FAF8F5] px-5 text-sm font-semibold text-[#111111] hover:bg-[#FFF4D6] sm:px-6"
        aria-label={`Copy ${label}`}
      >
        {copied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
}
