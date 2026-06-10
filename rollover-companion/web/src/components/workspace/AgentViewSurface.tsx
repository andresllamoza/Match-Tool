"use client";

import { JourneyFlow } from "@/components/JourneyFlow";
import { AgentSandboxPanel } from "@/components/sandbox/AgentSandboxPanel";
import { useWorkspace } from "@/context/JourneyWorkspaceContext";

export function AgentViewSurface() {
  const controller = useWorkspace();

  return (
    <section className="flex flex-col gap-3 text-left">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 2</p>
        <h2 className="text-lg font-bold text-[#111111]">The Agent View</h2>
      </div>

      <div className="flex flex-col gap-4 rounded-2xl border border-[#EAE5DC] bg-white p-6 shadow-sm">
        <header className="border-b border-[#EAE5DC] pb-4">
          <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
            BeeKeeper administration
          </p>
          <p className="mt-1 text-sm text-[#555555]">
            Live engine mirror — actions in Surface 1 update this panel instantly.
          </p>
        </header>

        {controller.data ? (
          <AgentSandboxPanel data={controller.data} />
        ) : (
          <div className="rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] p-4 text-sm text-[#6B6560]">
            Starting shared journey…
          </div>
        )}

        <div className="rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] p-4">
          <p className="mb-3 text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Live customer mirror (read-only)
          </p>
          <div className="rounded-xl border border-[#EAE5DC] bg-white p-4">
            <JourneyFlow
              mode="customer"
              surface="sandbox"
              channelSurface="agent"
              controller={controller}
              readOnly
              hideAssistant
            />
          </div>
        </div>
      </div>
    </section>
  );
}
