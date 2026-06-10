"use client";

import { JourneyFlow } from "@/components/JourneyFlow";
import { AgentSandboxPanel } from "@/components/sandbox/AgentSandboxPanel";
import { useWorkspace } from "@/context/JourneyWorkspaceContext";

export function AgentViewSurface() {
  const controller = useWorkspace();

  return (
    <section className="flex flex-col gap-6 text-left">
      <div className="space-y-1">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 2</p>
        <h2 className="text-xl font-bold text-[#1E242B]">The Agent View</h2>
        <p className="text-sm leading-relaxed text-[#555555]">
          BeeKeeper intel plus a read-only customer mirror with routing rationale.
        </p>
      </div>

      <div
        className={`flex flex-col gap-8 pb-surface-card transition-all duration-300 ${
          controller.escalationActive
            ? "animate-pulse-border rounded-2xl border-2 border-amber-400/80"
            : ""
        }`}
        onClick={controller.escalationActive ? () => controller.clearEscalationAlert() : undefined}
        role={controller.escalationActive ? "alert" : undefined}
      >
        <header className="border-b border-[#EAE5DC] pb-6">
          <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
            BeeKeeper administration
          </p>
          <p className="mt-2 text-sm leading-relaxed text-[#555555]">
            Live engine mirror — actions in Surface 1 update this panel instantly.
          </p>
          {controller.escalationActive && (
            <p className="mt-3 rounded-lg bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-900">
              New handoff — customer requested a BeeKeeper on step{" "}
              {(controller.stalledStep ?? controller.data?.step_index ?? 0) + 1}.
            </p>
          )}
        </header>

        {controller.data ? (
          <AgentSandboxPanel
            data={controller.data}
            pathHistory={controller.pathHistory}
            stalledStep={controller.stalledStep}
          />
        ) : (
          <div className="rounded-2xl border border-[#EAE5DC] bg-[#FAF8F5] px-6 py-8 text-sm text-[#6B6560]">
            Starting shared journey…
          </div>
        )}

        <div className="rounded-2xl border border-[#EAE5DC] bg-[#FAF8F5] p-6 sm:p-8">
          <p className="mb-4 text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Live customer mirror (read-only)
          </p>
          <div className="rounded-2xl border border-[#EAE5DC] bg-white p-6 sm:p-8">
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
