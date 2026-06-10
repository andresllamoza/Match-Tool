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
  const [smsSent, setSmsSent] = useState(false);

  const providerStatus = screen.has_reconstructed_content
    ? "RECONSTRUCTED"
    : intel.provider_status
      ? String(intel.provider_status).toUpperCase()
      : screen.provider
        ? "VERIFIED"
        : "PENDING LOOKUP";

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
      <div className="rounded-xl border border-[#F0E6D2] bg-[#FFF9EE] p-4 text-[#111111]">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          BeeKeeper live context
        </p>
        <dl className="mt-3 space-y-3 text-sm">
          <div>
            <dt className="font-semibold text-[#111111]">Provider Status</dt>
            <dd className="mt-0.5 font-medium text-[#1E242B]">{providerStatus}</dd>
            {screen.has_reconstructed_content && (
              <dd className="mt-1 text-xs text-[#6B6560]">
                Double-check phone menus with the customer before proceeding.
              </dd>
            )}
          </div>
          <div>
            <dt className="font-semibold text-[#111111]">Escalation Triggers</dt>
            <dd className="mt-0.5 text-[#1E242B]">
              {escalationTriggers.length > 0
                ? escalationTriggers.map((t) => `[${t}]`).join(" · ")
                : "[None active]"}
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-[#111111]">Agent Action Call Script</dt>
            <dd className="mt-0.5 font-medium leading-relaxed text-[#111111]">
              &ldquo;{agentScript}&rdquo;
            </dd>
          </div>
        </dl>
        <button
          type="button"
          onClick={() => setSmsSent(true)}
          className="mt-4 h-12 w-full rounded-xl bg-[#111111] text-sm font-semibold text-white transition active:scale-[0.99] hover:bg-[#1E242B]"
        >
          {smsSent ? "✓ Access recovery SMS queued" : "Send Access Recovery Instructions (SMS)"}
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-[#EAE5DC] bg-white">
        <div className="border-b border-[#EAE5DC] px-4 py-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-[#111111]">
            Knowledge Layer scripts
          </h3>
          <p className="mt-0.5 text-xs text-[#6B6560]">
            Provider playbook rules from the rollover knowledge layer
          </p>
        </div>
        <div className="divide-y divide-[#EAE5DC]">
          {knowledgeRules.length === 0 ? (
            <p className="px-4 py-4 text-sm text-[#6B6560]">
              Run an employer lookup in Surface 1 to load provider-specific scripts.
            </p>
          ) : (
            knowledgeRules.map((rule, i) => {
              const expanded = openRule === i;
              return (
                <div key={`${rule.title}-${i}`}>
                  <button
                    type="button"
                    onClick={() => setOpenRule(expanded ? null : i)}
                    className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-[#111111] transition hover:bg-[#FAF8F5]"
                    aria-expanded={expanded}
                  >
                    <span>{rule.title}</span>
                    <span className="text-[#6B6560]" aria-hidden>
                      {expanded ? "−" : "+"}
                    </span>
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
