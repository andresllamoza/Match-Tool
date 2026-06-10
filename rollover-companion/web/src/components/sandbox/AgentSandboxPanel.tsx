"use client";

import { useState } from "react";
import type { JourneyResponse } from "@/lib/types";

interface KnowledgeRule {
  title: string;
  body: string;
}

interface AgentSandboxPanelProps {
  data: JourneyResponse;
}

export function AgentSandboxPanel({ data }: AgentSandboxPanelProps) {
  const { screen, provider_intel: intel } = data;
  const [openRule, setOpenRule] = useState<number | null>(0);

  const providerStatus = screen.has_reconstructed_content
    ? "RECONSTRUCTED (Double-check with customer)"
    : intel.provider_status
      ? String(intel.provider_status)
      : screen.provider || screen.state === "provider_unknown"
        ? "PENDING LOOKUP"
        : "VERIFIED";

  const escalationTriggers = [
    ...(Array.isArray(intel.escalation_triggers) ? intel.escalation_triggers : []),
    ...(Array.isArray(intel.failure_modes) ? intel.failure_modes : []),
  ] as string[];

  const agentScript =
    screen.next_beekeeper_script ||
    (typeof intel.agent_action_script === "string" ? intel.agent_action_script : null) ||
    "Monitor customer progress and offer live BeeKeeper support when needed.";

  const knowledgeRules = (Array.isArray(intel.knowledge_rules)
    ? intel.knowledge_rules
    : []) as KnowledgeRule[];

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-[#F0E6D2] bg-[#FFF9EE] p-4">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          BeeKeeper live context
        </p>
        <dl className="mt-3 space-y-2 text-sm">
          <div>
            <dt className="font-semibold text-[#111111]">Provider Status</dt>
            <dd className="text-[#1E242B]">{providerStatus}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[#111111]">Escalation Triggers</dt>
            <dd className="text-[#1E242B]">
              {escalationTriggers.length > 0
                ? escalationTriggers.map((t) => `[${t}]`).join(" | ")
                : "[None active]"}
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-[#111111]">Agent Action Call Script</dt>
            <dd className="font-medium text-[#111111]">&ldquo;{agentScript}&rdquo;</dd>
          </div>
        </dl>
      </div>

      <div className="rounded-xl border border-[#EAE5DC] bg-white">
        <div className="border-b border-[#EAE5DC] px-4 py-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-[#111111]">
            Agent Knowledge Layer
          </h3>
          <p className="mt-0.5 text-xs text-[#6B6560]">
            Active provider rules pulled from the engine playbook
          </p>
        </div>
        <div className="divide-y divide-[#EAE5DC]">
          {knowledgeRules.length === 0 ? (
            <p className="px-4 py-4 text-sm text-[#6B6560]">
              Run an employer lookup to load provider-specific scripts and escalation paths.
            </p>
          ) : (
            knowledgeRules.map((rule, i) => {
              const expanded = openRule === i;
              return (
                <div key={`${rule.title}-${i}`}>
                  <button
                    type="button"
                    onClick={() => setOpenRule(expanded ? null : i)}
                    className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-[#111111] hover:bg-[#FAF8F5]"
                  >
                    <span>{rule.title}</span>
                    <span className="text-[#6B6560]">{expanded ? "−" : "+"}</span>
                  </button>
                  {expanded && (
                    <p className="px-4 pb-4 text-sm leading-relaxed text-[#555555]">{rule.body}</p>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
