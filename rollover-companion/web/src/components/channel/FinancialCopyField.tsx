"use client";

import { CopyMicroButton } from "./CopyMicroButton";

export function FinancialCopyField({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start justify-between gap-4 overflow-hidden rounded-xl border border-[#EAE5DC] bg-[#FDFDFD] px-6 py-5 shadow-sm sm:px-8 sm:py-6">
      <div className="min-w-0 flex-1">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          {label}
        </p>
        <p className="mt-2 break-words text-base font-semibold leading-snug text-[#1E242B] sm:text-lg">
          {value}
        </p>
      </div>
      <CopyMicroButton value={value} label={label} />
    </div>
  );
}
