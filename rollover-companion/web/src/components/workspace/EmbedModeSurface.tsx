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
    <section className="flex flex-col gap-3 text-left">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">Surface 3</p>
        <h2 className="text-lg font-bold text-[#111111]">The Embed Mode</h2>
      </div>

      <div className="flex flex-col gap-4 rounded-2xl border border-[#EAE5DC] bg-white p-6 shadow-sm">
        <div className="space-y-3 rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] p-4">
          <label className="block text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Theme variant
            <select
              value={embedTheme}
              onChange={(e) => setEmbedTheme(e.target.value as EmbedTheme)}
              className="mt-1.5 w-full rounded-xl border border-[#EAE5DC] bg-white px-3 py-2.5 text-sm font-medium text-[#111111] outline-none focus:border-2 focus:border-[#111111]"
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
              className="mt-1.5 w-full rounded-xl border border-[#EAE5DC] bg-white px-3 py-2.5 text-sm text-[#111111] outline-none focus:border-2 focus:border-[#111111]"
              placeholder="/api/journey"
            />
          </label>
        </div>

        <div className="rounded-2xl bg-[#1E242B] p-6">
          <p className="mb-3 text-xs font-bold uppercase tracking-wider text-white/50">
            Simulated device frame
          </p>
          <div className="overflow-hidden rounded-xl border border-white/10 bg-[#1E242B]">
            <JourneyFlow
              mode="embed"
              theme={embedTheme === "dark" ? "dark" : "minimal"}
              surface="sandbox"
              controller={controller}
              readOnly
              hideAssistant
            />
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Frame embed code
          </p>
          <pre className="overflow-x-auto rounded-xl border border-[#EAE5DC] bg-[#111111] p-4 text-xs leading-relaxed text-[#FAF8F5]">
            {mountCode}
          </pre>
        </div>

        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            API action example
          </p>
          <pre className="overflow-x-auto rounded-xl border border-[#EAE5DC] bg-[#111111] p-4 text-xs leading-relaxed text-[#FAF8F5]">
            {apiSnippet}
          </pre>
          <p className="mt-2 text-xs text-[#6B6560]">
            Theme: <span className="font-semibold text-[#111111]">{mountTheme}</span>
            {" · "}
            Journey: <span className="font-mono text-[#111111]">{journeyId}</span>
          </p>
        </div>
      </div>
    </section>
  );
}
