import type { ScreenEnrichment } from "@/lib/types";
import { NextStepBadge } from "./ui/NextStepBadge";

const TRACK_STEPS = [
  { id: "sent", label: "Provider sends your rollover" },
  { id: "transit", label: "Check or transfer in transit" },
  { id: "landed", label: "Funds land in your PensionBee IRA" },
] as const;

export function TrackPanel({ enrichment }: { enrichment: ScreenEnrichment }) {
  const track = enrichment.track;
  if (!track) return null;

  return (
    <div className="mb-5 rounded-card border border-bee-border bg-cream-dark/50 p-5 lg:p-6">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-bee-charcoal">
          What to expect
        </h3>
        <NextStepBadge>Track</NextStepBadge>
      </div>

      <ol className="mb-6 space-y-0 border-l-2 border-bee-border pl-6">
        {TRACK_STEPS.map((step, i) => {
          const isDone = i === 0;
          const isCurrent = i === 1;
          const isLast = i === TRACK_STEPS.length - 1;

          return (
            <li key={step.id} className="relative pb-6 last:pb-0">
              <span
                className={`absolute -left-[1.65rem] top-0 flex h-7 w-7 items-center justify-center rounded-full border-2 ${
                  isDone
                    ? "border-bee-charcoal bg-bee-charcoal text-white"
                    : isCurrent
                      ? "animate-pulse-border border-bee-yellow bg-bee-yellow text-bee-charcoal"
                      : "border-bee-border bg-white text-bee-muted"
                }`}
                aria-hidden
              >
                {isDone ? (
                  <svg className="h-3.5 w-3.5" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M3 8.5L6.5 12L13 4"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                ) : (
                  <span className="text-[10px] font-bold">{i + 1}</span>
                )}
              </span>
              <p
                className={`text-sm font-semibold lg:text-base ${
                  isCurrent ? "text-bee-charcoal" : isDone ? "text-bee-muted" : "text-bee-faint"
                }`}
              >
                {step.label}
              </p>
              {isLast && (
                <p className="mt-1 text-xs leading-relaxed text-bee-muted">
                  Eligible rollovers earn a 1% match once funds arrive.
                </p>
              )}
            </li>
          );
        })}
      </ol>

      <dl className="space-y-3 border-t border-bee-border pt-4 text-sm lg:text-base">
        <div>
          <dt className="font-semibold text-bee-muted">Timeline</dt>
          <dd className="text-bee-ink">{track.typical_timeline}</dd>
        </div>
        <div>
          <dt className="font-semibold text-bee-muted">Check destination</dt>
          <dd className="text-bee-ink">{track.check_destination}</dd>
        </div>
        {track.mechanism_note && (
          <div>
            <dt className="font-semibold text-bee-muted">Path</dt>
            <dd className="text-bee-ink">{track.mechanism_note}</dd>
          </div>
        )}
      </dl>
      <div className="mt-4 rounded-block border border-bee-border bg-white px-4 py-3 text-sm text-bee-ink lg:text-base">
        <span className="font-semibold text-bee-charcoal">Day {track.follow_up_days}:</span>{" "}
        {track.nothing_arrived_message}
      </div>
    </div>
  );
}
