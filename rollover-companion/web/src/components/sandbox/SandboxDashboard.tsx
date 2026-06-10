"use client";

import { useState } from "react";
import { BrandHeader } from "@/components/BrandHeader";
import { JourneyFlow } from "@/components/JourneyFlow";
import { useJourneyController } from "@/hooks/useJourneyController";
import { AgentSandboxPanel } from "./AgentSandboxPanel";

type EmbedTheme = "light" | "dark";

export function SandboxDashboard() {
  const [embedTheme, setEmbedTheme] = useState<EmbedTheme>("light");
  const [apiEndpoint, setApiEndpoint] = useState("/api/journey");
  const controller = useJourneyController({ withAgentIntel: true });

  const journeyId = controller.data?.context.journey_id ?? "…";
  const mountTheme = embedTheme === "light" ? "LIGHT (PensionBee)" : "DARK (Custom Partner)";
  const mountCode = `<iframe
  src="${typeof window !== "undefined" ? window.location.origin : "https://your-host"}/embed?employer="
  component="RolloverCompanion"
  theme="${embedTheme === "light" ? "LIGHT" : "DARK"}"
  api="${apiEndpoint}"
  journeyId="${journeyId}"
/>`;

  return (
    <div className="min-h-dvh bg-[#FAF8F5]">
      <div className="border-b border-[#EAE5DC] bg-white px-4 py-4 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4">
          <BrandHeader mode="agent" />
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-[#111111] px-3 py-1 text-xs font-bold text-white">
              Production Sandbox
            </span>
            <button
              type="button"
              onClick={() => controller.restart()}
              disabled={controller.loading}
              className="flex h-11 w-11 items-center justify-center rounded-xl border border-[#EAE5DC] bg-white text-lg text-[#111111] transition hover:border-[#111111] disabled:opacity-50"
              title="Restart shared journey"
            >
              ↺
            </button>
          </div>
        </div>
        <p className="mx-auto mt-2 max-w-[1600px] text-sm text-[#6B6560]">
          Three synchronized engine surfaces — customer, BeeKeeper agent, and partner embed — bound
          to one live journey state.
        </p>
      </div>

      <div className="mx-auto grid max-w-[1600px] gap-6 px-4 py-6 sm:px-6 lg:grid-cols-3 lg:px-8 lg:py-8">
        {/* Column 1 — Customer */}
        <section className="flex flex-col gap-3">
          <header>
            <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 1</p>
            <h2 className="text-lg font-bold text-[#111111]">The Customer Flow</h2>
          </header>
          <div className="flex-1 rounded-2xl border border-[#EAE5DC] bg-[#FAF8F5] p-4 shadow-sm">
            <JourneyFlow mode="customer" controller={controller} />
          </div>
        </section>

        {/* Column 2 — Agent */}
        <section className="flex flex-col gap-3">
          <header>
            <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 2</p>
            <h2 className="text-lg font-bold text-[#111111]">The Agent View</h2>
          </header>
          <div className="flex-1 space-y-4 rounded-2xl border border-[#EAE5DC] bg-white p-4 shadow-sm">
            {controller.data && <AgentSandboxPanel data={controller.data} />}
            <div className="rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] p-3">
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[#6B6560]">
                Live customer mirror
              </p>
              <JourneyFlow
                mode="customer"
                controller={controller}
                readOnly
                hideAssistant
              />
            </div>
          </div>
        </section>

        {/* Column 3 — Embed */}
        <section className="flex flex-col gap-3">
          <header>
            <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 3</p>
            <h2 className="text-lg font-bold text-[#111111]">The Embed Mode</h2>
          </header>
          <div className="flex-1 rounded-2xl border border-[#EAE5DC] bg-white p-4 shadow-sm">
            <div className="mb-4 space-y-3 rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] p-4">
              <label className="block text-xs font-bold uppercase tracking-wide text-[#6B6560]">
                Theme Variant
                <select
                  value={embedTheme}
                  onChange={(e) => setEmbedTheme(e.target.value as EmbedTheme)}
                  className="mt-1 w-full rounded-lg border border-[#EAE5DC] bg-white px-3 py-2 text-sm text-[#111111]"
                >
                  <option value="light">LIGHT (PensionBee)</option>
                  <option value="dark">DARK (Custom Partner)</option>
                </select>
              </label>
              <label className="block text-xs font-bold uppercase tracking-wide text-[#6B6560]">
                Mount API Endpoint
                <input
                  value={apiEndpoint}
                  onChange={(e) => setApiEndpoint(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-[#EAE5DC] bg-white px-3 py-2 text-sm text-[#111111]"
                  placeholder="/api/journey"
                />
              </label>
            </div>

            <div className="rounded-2xl bg-[#1E242B] p-6">
              <p className="mb-3 text-xs font-bold uppercase tracking-wider text-white/60">
                Live preview window
              </p>
              <div className="overflow-hidden rounded-xl border border-white/10 bg-[#1E242B]">
                <JourneyFlow
                  mode="embed"
                  theme={embedTheme === "dark" ? "dark" : "minimal"}
                  controller={controller}
                  readOnly
                  hideAssistant
                />
              </div>
            </div>

            <div className="mt-4">
              <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[#6B6560]">
                Mount code
              </p>
              <pre className="overflow-x-auto rounded-xl border border-[#EAE5DC] bg-[#111111] p-4 text-xs leading-relaxed text-[#FAF8F5]">
                {mountCode}
              </pre>
              <p className="mt-2 text-xs text-[#6B6560]">
                Theme: <code className="text-[#111111]">{mountTheme}</code> · Journey:{" "}
                <code className="text-[#111111]">{journeyId}</code>
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
