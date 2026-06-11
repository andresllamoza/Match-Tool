import type { JourneyPhase } from "@/lib/types";

const STEPS: { id: JourneyPhase; label: string }[] = [
  { id: "find", label: "Find" },
  { id: "access", label: "Access" },
  { id: "rollover", label: "Roll over" },
  { id: "track", label: "Track" },
];

interface ProgressStepsProps {
  current: JourneyPhase;
  variant?: "default" | "minimal";
}

export function ProgressSteps({ current, variant = "default" }: ProgressStepsProps) {
  const currentIdx = STEPS.findIndex((s) => s.id === current);

  if (variant === "minimal") {
    return (
      <nav aria-label="Rollover progress" className="mb-8 flex gap-6 sm:gap-8">
        {STEPS.map((step, i) => {
          const active = i === currentIdx;
          return (
            <div key={step.id} className="inline-flex flex-col items-start">
              <span
                className={`text-[11px] font-bold uppercase tracking-[0.2em] ${
                  active ? "text-bee-charcoal" : "text-bee-muted"
                }`}
              >
                {step.label}
              </span>
              {active && (
                <span className="mt-2 h-[3px] w-full rounded-full bg-bee-yellow" aria-hidden />
              )}
            </div>
          );
        })}
      </nav>
    );
  }

  return (
    <div className="mb-6 lg:mb-8">
      <div className="flex items-center justify-between gap-1">
        {STEPS.map((step, i) => {
          const done = i < currentIdx;
          const active = i === currentIdx;
          return (
            <div key={step.id} className="flex flex-1 flex-col items-center gap-2">
              <div className="flex w-full items-center">
                {i > 0 && (
                  <div
                    className={`h-0.5 flex-1 ${done || active ? "bg-bee-yellow" : "bg-bee-border"}`}
                  />
                )}
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors lg:h-10 lg:w-10 lg:text-sm ${
                    done
                      ? "bg-bee-charcoal text-white"
                      : active
                        ? "bg-bee-yellow text-bee-charcoal ring-4 ring-bee-yellow/30"
                        : "border border-bee-border bg-cream-dark text-bee-muted"
                  }`}
                >
                  {done ? (
                    <svg className="h-4 w-4" viewBox="0 0 16 16" fill="none" aria-hidden>
                      <path
                        d="M3 8.5L6.5 12L13 4"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  ) : (
                    i + 1
                  )}
                </div>
                {i < STEPS.length - 1 && (
                  <div
                    className={`h-0.5 flex-1 ${done ? "bg-bee-yellow" : "bg-bee-border"}`}
                  />
                )}
              </div>
              <span
                className={`text-[11px] font-bold uppercase tracking-[0.2em] ${
                  active ? "text-bee-charcoal" : "text-bee-muted"
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
