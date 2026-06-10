import { BrandHeader } from "@/components/BrandHeader";
import { JourneyFlow } from "@/components/JourneyFlow";

export default function AgentPage() {
  return (
    <main className="mx-auto min-h-dvh max-w-desktop bg-canvas px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
      <BrandHeader mode="agent" />
      <div className="mb-6 rounded-xl border border-bee-border bg-white px-4 py-3 lg:mb-8 lg:px-5">
        <p className="text-xs font-bold uppercase tracking-wider text-bee-muted">Internal · BeeKeeper</p>
        <p className="mt-1 text-sm text-bee-ink lg:text-base">
          Same live journey as the customer — with provider intel, scripts, and escalation triggers.
        </p>
      </div>
      <JourneyFlow mode="agent" />
    </main>
  );
}
