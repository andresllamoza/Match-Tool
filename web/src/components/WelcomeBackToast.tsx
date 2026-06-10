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
  return (
    <div
      className="fixed inset-x-0 bottom-0 z-[60] flex justify-center px-4 pb-6 sm:px-6"
      role="status"
      aria-live="polite"
    >
      <div className="animate-toast-up w-full max-w-lg rounded-2xl border border-[#EAE5DC] bg-white p-6 shadow-[0_12px_48px_rgba(17,17,17,0.14)] sm:p-8">
        <p className="text-xs font-bold uppercase tracking-wider text-[#9A6200]">
          Welcome back
        </p>
        <p className="mt-2 text-base leading-relaxed text-[#1E242B] sm:text-lg">
          We saved your progress moving your{" "}
          <span className="font-semibold text-[#111111]">{providerName}</span> 401(k).
        </p>
        <div className="mt-6 space-y-3">
          <Button onClick={onResume} disabled={loading}>
            {loading ? "Restoring…" : `Resume Step ${stepNumber}`}
          </Button>
          <button
            type="button"
            onClick={onStartOver}
            disabled={loading}
            className="pb-interactive w-full py-3 text-center text-sm font-semibold text-[#6B6560] hover:text-[#1E242B] disabled:opacity-50"
          >
            Start over
          </button>
        </div>
      </div>
    </div>
  );
}
