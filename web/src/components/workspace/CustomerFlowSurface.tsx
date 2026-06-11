"use client";

import { JourneyFlow } from "@/components/JourneyFlow";
import { BeeMark } from "@/components/ui/BeeMark";
import { useWorkspace } from "@/context/JourneyWorkspaceContext";

function SurfaceCardHeader({
  onRestart,
  loading,
}: {
  onRestart: () => void;
  loading: boolean;
}) {
  return (
    <header className="mb-8 flex items-center justify-between gap-4 border-b border-[#EAE5DC] pb-6">
      <div className="flex items-center gap-4">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-bee-yellow text-bee-charcoal">
          <BeeMark className="h-5 w-5" />
        </div>
        <div className="text-left">
          <p className="text-base font-bold text-[#111111]">PensionBee</p>
          <p className="text-sm text-[#6B6560]">Rollover Companion</p>
        </div>
      </div>
      <button
        type="button"
        onClick={onRestart}
        disabled={loading}
        title="Restart journey"
        className="pb-interactive flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-[#EAE5DC] bg-white text-lg text-[#111111] hover:border-[#111111] disabled:opacity-50"
      >
        ↺
      </button>
    </header>
  );
}

export function CustomerFlowSurface() {
  const controller = useWorkspace();

  return (
    <section className="flex flex-col gap-6 text-left">
      <div className="space-y-1">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 1</p>
        <h2 className="text-xl font-bold text-[#1E242B]">The Customer Flow</h2>
        <p className="text-sm leading-relaxed text-[#555555]">
          Primary experience — conversational scripts and copy-ready routing fields.
        </p>
      </div>

      <div className="pb-surface-card min-h-[640px]">
        <SurfaceCardHeader onRestart={() => controller.restart()} loading={controller.loading} />
        <JourneyFlow mode="customer" surface="sandbox" controller={controller} />
      </div>
    </section>
  );
}
