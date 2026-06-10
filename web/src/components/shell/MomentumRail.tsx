"use client";

import { motion } from "framer-motion";
import type { JourneyPhase } from "@/lib/types";

const SEGMENTS: { id: JourneyPhase; label: string }[] = [
  { id: "find", label: "Find" },
  { id: "access", label: "Access" },
  { id: "rollover", label: "Roll over" },
  { id: "track", label: "Track" },
];

export function MomentumRail({ phase }: { phase: JourneyPhase }) {
  const idx = Math.max(0, SEGMENTS.findIndex((s) => s.id === phase));

  return (
    <nav className="mb-6 flex gap-3" aria-label="Journey progress">
      {SEGMENTS.map((seg, i) => {
        const done = i < idx;
        const active = i === idx;
        return (
          <div key={seg.id} className="flex flex-1 flex-col">
            <div className="relative h-1 overflow-hidden rounded-full bg-cream-deeper">
              {active && (
                <motion.div
                  className="absolute inset-y-0 left-0 rounded-full bg-bee-yellow"
                  layoutId="momentum-fill"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  style={{ width: "100%" }}
                />
              )}
              {done && <div className="absolute inset-0 rounded-full bg-bee-charcoal" />}
            </div>
            <span
              className={`mt-2 text-[10px] font-bold uppercase tracking-[0.08em] ${
                active ? "text-bee-charcoal" : done ? "text-bee-charcoal/70" : "text-bee-muted"
              }`}
            >
              {seg.label}
            </span>
          </div>
        );
      })}
    </nav>
  );
}
