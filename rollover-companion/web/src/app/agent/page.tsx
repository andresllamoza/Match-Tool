import { BrandHeader } from "@/components/BrandHeader";
import { JourneyFlow } from "@/components/JourneyFlow";

export default function AgentPage() {
  return (
    <main className="mx-auto min-h-dvh max-w-desktop px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
      <BrandHeader mode="agent" />
      <div className="mb-4 flex items-center gap-2 lg:mb-6">
        <span className="rounded-pill bg-bee-blue px-3 py-1 text-xs font-bold text-white">
          BeeKeeper view
        </span>
        <span className="text-sm text-bee-muted lg:text-base">
          Same journey as the customer — with intel, scripts, and escalation triggers.
        </span>
      </div>
      <JourneyFlow mode="agent" />
    </main>
  );
}
