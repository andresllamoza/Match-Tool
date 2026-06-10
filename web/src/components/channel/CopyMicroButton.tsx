"use client";

import { useState } from "react";

export function CopyMicroButton({
  value,
  label,
}: {
  value: string;
  label: string;
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
    <button
      type="button"
      onClick={copy}
      aria-label={`Copy ${label}`}
      className={`pb-interactive inline-flex shrink-0 items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all duration-200 ease-out ${
        copied
          ? "text-emerald-600"
          : "text-[#6B6560] hover:bg-[#FAF8F5] hover:text-[#1E242B]"
      }`}
    >
      {copied ? (
        <span className="text-sm leading-none" aria-hidden>
          ✓
        </span>
      ) : (
        "Copy"
      )}
    </button>
  );
}
