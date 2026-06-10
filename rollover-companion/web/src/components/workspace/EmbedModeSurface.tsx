"use client";

import { useState } from "react";
import { JourneyFlow } from "@/components/JourneyFlow";
import { useWorkspace } from "@/context/JourneyWorkspaceContext";

type EmbedTheme = "light" | "dark";

export function EmbedModeSurface() {
  const controller = useWorkspace();
  const [embedTheme, setEmbedTheme] = useState<EmbedTheme>("light");
  const [apiEndpoint, setApiEndpoint] = useState("/api/journey");

  const journeyId = controller.data?.context.journey_id ?? "…";
  const origin = typeof window !== "undefined" ? window.location.origin : "https://your-host";
  const mountTheme = embedTheme === "light" ? "LIGHT (PensionBee)" : "DARK (Custom Partner)";

  const mountCode = `<iframe
  src="${origin}/embed?theme=${embedTheme}"
  title="PensionBee Rollover Companion"
  style="width:100%;min-height:640px;border:none;border-radius:16px"
  allow="clipboard-write"
/>`;

  const apiSnippet = `// POST ${apiEndpoint}
{
  "journey_id": "${journeyId}",
  "type": "lookup",
  "employer": "Google"
}`;

  return (
    <section className="flex flex-col gap-6 text-left">
      <div className="space-y-1">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 3</p>
        <h2 className="text-xl font-bold text-[#1E242B]">The Embed Mode</h2>
        <p className="text-sm leading-relaxed text-[#555555]">
          Narrow-viewport frame with identical step engine data and partner theming.
        </p>
      </div>

      <div className="flex flex-col gap-8 pb-surface-card">
        <div className="space-y-6 rounded-2xl border border-[#EAE5DC] bg-[#FAF8F5] p-6 sm:p-8">
          <label className="block text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Theme variant
            <select
              value={embedTheme}
              onChange={(e) => setEmbedTheme(e.target.value as EmbedTheme)}
              className="pb-interactive mt-2 w-full rounded-xl border border-[#EAE5DC] bg-white px-4 py-3 text-sm font-medium text-[#1E242B] outline-none transition-all focus:border-2 focus:border-[#111111]"
            >
              <option value="light">LIGHT (PensionBee)</option>
              <option value="dark">DARK (Custom Partner)</option>
            </select>
          </label>

          <label className="block text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Mount API endpoint
            <input
              value={apiEndpoint}
              onChange={(e) => setApiEndpoint(e.target.value)}
              className="mt-2 w-full rounded-xl border border-[#EAE5DC] bg-white px-4 py-3 text-sm text-[#1E242B] outline-none transition-all focus:border-2 focus:border-[#111111]"
              placeholder="/api/journey"
            />
          </label>
        </div>

        <div className="rounded-2xl bg-[#1E242B] p-6 sm:p-8">
          <p className="mb-4 text-xs font-bold uppercase tracking-wider text-white/50">
            Simulated device frame
          </p>
          <div className="overflow-hidden rounded-xl border border-white/10">
            <JourneyFlow
              key={embedTheme}
              mode="embed"
              theme={embedTheme === "dark" ? "dark" : "minimal"}
              surface="sandbox"
              controller={controller}
              readOnly
              hideAssistant
            />
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Frame embed code
          </p>
          <pre className="overflow-x-auto rounded-2xl border border-[#EAE5DC] bg-[#111111] p-6 text-xs leading-relaxed text-[#FAF8F5]">
            {mountCode}
          </pre>
        </div>

        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            API action example
          </p>
          <pre className="overflow-x-auto rounded-2xl border border-[#EAE5DC] bg-[#111111] p-6 text-xs leading-relaxed text-[#FAF8F5]">
            {apiSnippet}
          </pre>
          <p className="text-xs text-[#6B6560]">
            Theme: <span className="font-semibold text-[#1E242B]">{mountTheme}</span>
            {" · "}
            Journey: <span className="font-mono text-[#1E242B]">{journeyId}</span>
          </p>
        </div>
      </div>
    </section>
  );
}
