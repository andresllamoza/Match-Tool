"use client";

import { JourneyFlow } from "./JourneyFlow";
import { BrandHeader } from "./BrandHeader";

interface EmbedWidgetProps {
  theme?: "default" | "minimal";
  initialEmployer?: string;
}

/** Mountable embed — use via iframe or direct React import. */
export function EmbedWidget({ theme = "minimal", initialEmployer = "" }: EmbedWidgetProps) {
  return (
    <div className="min-h-[32rem] rounded-card border border-bee-border bg-canvas p-4 sm:p-6">
      <BrandHeader mode="embed" compact />
      <JourneyFlow mode="customer" theme={theme} initialEmployer={initialEmployer} />
    </div>
  );
}
