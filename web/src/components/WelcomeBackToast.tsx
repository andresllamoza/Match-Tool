"use client";

import { Button } from "./ui/Button";

export function WelcomeBackToast({
  providerName,
  stepNumber,
  loading,
  onResume,
  onStartOver,
}: {
  providerName: string;
  stepNumber: number;
  loading?: boolean;
  onResume: () => void;
  onStartOver: () => void;
}) {
  const planLabel = providerName.toLowerCase().includes("401")
    ? providerName
    : `${providerName} 401(k)`;

  return (
    <div
      className="fixed inset-x-0 bottom-0 z-[60] flex justify-center px-4 pb-6 sm:px-6"
      role="status"
      aria-live="polite"
    >
      <div className="animate-toast-up w-full max-w-lg rounded-card border border-bee-border bg-white p-6 shadow-card-lg sm:p-8">
        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-gold">
          Welcome back
        </p>
        <p className="mt-2 text-base leading-relaxed text-bee-ink sm:text-lg">
          We saved your progress on{" "}
          <span className="font-semibold text-bee-charcoal">{planLabel}</span>.
        </p>
        <div className="mt-6 space-y-3">
          <Button onClick={onResume} disabled={loading}>
            {loading ? "Restoring…" : `Resume Step ${stepNumber}`}
          </Button>
          <button
            type="button"
            onClick={onStartOver}
            disabled={loading}
            className="pb-text-link"
          >
            Start over
          </button>
        </div>
      </div>
    </div>
  );
}
