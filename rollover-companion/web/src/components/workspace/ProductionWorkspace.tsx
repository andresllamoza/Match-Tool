"use client";

import { useJourneyController } from "@/hooks/useJourneyController";
import { JourneyWorkspaceProvider } from "@/context/JourneyWorkspaceContext";
import { AgentViewSurface } from "./AgentViewSurface";
import { CustomerFlowSurface } from "./CustomerFlowSurface";
import { EmbedModeSurface } from "./EmbedModeSurface";

export function ProductionWorkspace() {
  const controller = useJourneyController({ withAgentIntel: true });

  return (
    <JourneyWorkspaceProvider value={controller}>
      <div className="min-h-screen bg-[#FAF8F5]">
        <div className="mx-auto max-w-[1700px] p-8">
          <header className="mb-8 text-left">
            <div className="mb-4 flex flex-wrap items-center gap-3">
              <span className="rounded-full bg-[#111111] px-3 py-1 text-xs font-bold text-white">
                Production Sandbox
              </span>
              {controller.data && (
                <span className="text-xs text-[#6B6560]">
                  Journey{" "}
                  <code className="rounded bg-white px-1.5 py-0.5 font-mono text-[#111111]">
                    {controller.data.context.journey_id}
                  </code>
                </span>
              )}
            </div>
            <h1 className="mb-2 text-4xl font-bold tracking-tight text-[#111111]">
              3-Surface Production Workspace
            </h1>
            <p className="max-w-3xl text-base text-[#555555]">
              Tell us your former employer or plan provider. We&apos;ll handle the lookup to locate
              your exact routing details.
            </p>
          </header>

          <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
            <CustomerFlowSurface />
            <AgentViewSurface />
            <EmbedModeSurface />
          </div>
        </div>
      </div>
    </JourneyWorkspaceProvider>
  );
}
