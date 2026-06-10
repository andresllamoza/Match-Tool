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
        <div className="mx-auto max-w-[1760px] px-6 py-10 sm:px-8 sm:py-12 lg:px-10">
          <header className="mb-12 text-left">
            <div className="mb-6 flex flex-wrap items-center gap-3">
              <span className="rounded-full bg-[#111111] px-4 py-1.5 text-xs font-bold text-white">
                Production Sandbox
              </span>
              {controller.data && (
                <span className="text-sm text-[#6B6560]">
                  Journey{" "}
                  <code className="rounded-lg bg-white px-2 py-1 font-mono text-xs text-[#1E242B] shadow-sm">
                    {controller.data.context.journey_id}
                  </code>
                </span>
              )}
            </div>
            <h1 className="mb-3 text-3xl font-bold tracking-tight text-[#111111] sm:text-4xl">
              3-Surface Production Workspace
            </h1>
            <p className="max-w-3xl text-base leading-relaxed text-[#555555] sm:text-lg">
              Tell us your former employer or plan provider. We&apos;ll handle the lookup to locate
              your exact routing details — mirrored live across customer, agent, and embed surfaces.
            </p>
          </header>

          <div className="grid grid-cols-1 gap-10 xl:grid-cols-3 xl:gap-12">
            <CustomerFlowSurface />
            <AgentViewSurface />
            <EmbedModeSurface />
          </div>
        </div>
      </div>
    </JourneyWorkspaceProvider>
  );
}
