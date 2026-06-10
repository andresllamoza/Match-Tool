"use client";

import { JourneyFlow } from "@/components/JourneyFlow";
import { useWorkspace } from "@/context/JourneyWorkspaceContext";

function SurfaceCardHeader({
  onRestart,
  loading,
}: {
  onRestart: () => void;
  loading: boolean;
}) {
  return (
    <header className="mb-6 flex items-center justify-between gap-4 border-b border-[#EAE5DC] pb-5">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#FFC72C] text-lg font-bold text-[#111111]">
          🐝
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
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-[#EAE5DC] bg-white text-lg text-[#111111] transition hover:border-[#111111] active:scale-[0.98] disabled:opacity-50"
      >
        ↺
      </button>
    </header>
  );
}

export function CustomerFlowSurface() {
  const controller = useWorkspace();

  return (
    <section className="flex flex-col gap-3 text-left">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 1</p>
        <h2 className="text-lg font-bold text-[#111111]">The Customer Flow</h2>
      </div>

      <div className="rounded-2xl border border-[#EAE5DC] bg-white p-8 shadow-sm">
        <SurfaceCardHeader onRestart={() => controller.restart()} loading={controller.loading} />
        <JourneyFlow mode="customer" surface="sandbox" controller={controller} />
      </div>
    </section>
  );
}
