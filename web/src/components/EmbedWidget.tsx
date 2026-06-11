"use client";

import { JourneyFlow } from "./JourneyFlow";
import { BrandHeader } from "./BrandHeader";

interface EmbedWidgetProps {
  theme?: "default" | "minimal" | "dark";
  initialEmployer?: string;
  initialProvider?: string;
}

/** Mountable embed — use via iframe or direct React import. */
export function EmbedWidget({
  theme = "minimal",
  initialEmployer = "",
  initialProvider = "",
}: EmbedWidgetProps) {
  const shell =
    theme === "dark"
      ? "min-h-[32rem] rounded-2xl border border-white/10 bg-[#1E242B] p-4 sm:p-6"
      : "min-h-[32rem] rounded-card border border-bee-border bg-canvas p-4 sm:p-6";

  return (
    <div className={shell}>
      <BrandHeader mode="embed" compact />
      <JourneyFlow
        mode="customer"
        theme={theme}
        initialEmployer={initialEmployer}
        initialProvider={initialProvider}
      />
    </div>
  );
}
