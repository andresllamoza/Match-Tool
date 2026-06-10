import type { JourneyPhase } from "../types/journey";

const SEGMENTS: { id: JourneyPhase; label: string }[] = [
  { id: "find", label: "Find" },
  { id: "access", label: "Access" },
  { id: "rollover", label: "Roll over" },
  { id: "track", label: "Track" },
];

export function MomentumRail({ phase }: { phase: JourneyPhase }) {
  const idx = SEGMENTS.findIndex((s) => s.id === phase);
  return (
    <nav className="mb-8 flex gap-2" aria-label="Journey progress">
      {SEGMENTS.map((seg, i) => {
        const done = i < idx;
        const active = i === idx;
        return (
          <div key={seg.id} className="flex flex-1 flex-col">
            <div
              className={`h-1 rounded-full ${
                active ? "bg-bee" : done ? "bg-ink" : "bg-[#D8D3C8]"
              }`}
            />
            <span
              className={`mt-2 text-[10px] font-bold uppercase tracking-wider ${
                active ? "text-ink" : done ? "text-ink/70" : "text-muted"
              }`}
            >
              {seg.label}
            </span>
            {active && <div className="mt-1 h-6 rounded-sm bg-bee/10" aria-hidden />}
          </div>
        );
      })}
    </nav>
  );
}
