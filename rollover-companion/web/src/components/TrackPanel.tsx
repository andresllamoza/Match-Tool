import type { ScreenEnrichment } from "@/lib/types";

export function TrackPanel({ enrichment }: { enrichment: ScreenEnrichment }) {
  const track = enrichment.track;
  if (!track) return null;

  return (
    <div className="mb-5 space-y-3 rounded-card border border-bee-border bg-cream-dark/50 p-5 lg:p-6">
      <h3 className="text-sm font-bold uppercase tracking-wide text-bee-blue">What to expect</h3>
      <dl className="space-y-3 text-sm lg:text-base">
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
      <div className="rounded-card bg-white px-4 py-3 text-sm text-bee-ink lg:text-base">
        <span className="font-semibold text-bee-blue">Day {track.follow_up_days}:</span>{" "}
        {track.nothing_arrived_message}
      </div>
    </div>
  );
}
