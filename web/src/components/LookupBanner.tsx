"use client";

import { useState } from "react";
import type { JourneyResponse } from "@/lib/types";
import { NextStepBadge } from "./ui/NextStepBadge";

const TIER_LABEL: Record<string, string> = {
  high: "High confidence",
  medium: "Likely match",
  low: "Still narrowing it down",
};

const GUIDE_VISIBLE_STATES = new Set([
  "provider_identified",
  "provider_not_covered",
  "access_recovered",
  "access_blocked",
]);

export function LookupBanner({ data }: { data: JourneyResponse }) {
  const [expanded, setExpanded] = useState(false);
  const { screen, enrichment, context } = data;
  const provider = screen.provider || context.uncovered_provider;
  if (!provider || !GUIDE_VISIBLE_STATES.has(screen.state)) return null;

  const tier = screen.confidence_tier || context.lookup_confidence_tier;
  const employer = enrichment.lookup?.employer_query || context.employer_query;
  const lookup = enrichment.lookup;

  return (
    <div className="mb-5 rounded-card border-2 border-bee-yellow/40 bg-bee-yellow-tint p-5 lg:p-6">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        {tier && (
          <span className="inline-block rounded-pill bg-bee-charcoal px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-white">
            {TIER_LABEL[tier] || tier}
          </span>
        )}
        {screen.state === "provider_identified" && (
          <NextStepBadge>Next: confirm access</NextStepBadge>
        )}
        {screen.state === "access_recovered" && enrichment.requires_tax_selection && (
          <NextStepBadge>Next: fund type</NextStepBadge>
        )}
        {screen.state === "access_recovered" && !enrichment.requires_tax_selection && (
          <NextStepBadge>Next: choose channel</NextStepBadge>
        )}
      </div>

      <dl className="space-y-3">
        <div>
          <dt className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
            {enrichment.general_path ? "Recordkeeper" : "Matched provider"}
          </dt>
          <dd className="mt-1 text-xl font-extrabold tracking-[-0.02em] text-bee-charcoal">
            {provider}
          </dd>
        </div>
        {employer && (
          <div>
            <dt className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
              Based on
            </dt>
            <dd className="mt-1 text-sm text-bee-ink">{employer}</dd>
          </div>
        )}
        {enrichment.provider_portal && (
          <div>
            <dt className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
              Portal
            </dt>
            <dd className="mt-1 text-sm font-semibold text-bee-ink">{enrichment.provider_portal}</dd>
          </div>
        )}
        {enrichment.preferred_path && (
          <div>
            <dt className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
              PensionBee path
            </dt>
            <dd className="mt-1 text-sm leading-relaxed text-bee-ink">{enrichment.preferred_path}</dd>
          </div>
        )}
        {enrichment.check_destination && !enrichment.preferred_path && (
          <div>
            <dt className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
              Check path
            </dt>
            <dd className="mt-1 text-sm text-bee-ink">{enrichment.check_destination}</dd>
          </div>
        )}
      </dl>

      {lookup && (
        <div className="mt-4 border-t border-bee-border pt-4">
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="pb-text-link min-h-[44px] justify-start py-2 text-left text-sm"
          >
            {expanded ? "Hide match details" : "Why we matched this →"}
          </button>
          {expanded && (
            <dl className="mt-2 space-y-2 text-sm text-bee-ink">
              <div>
                <dt className="font-semibold text-bee-muted">Employer searched</dt>
                <dd>{lookup.employer_query}</dd>
              </div>
              <div>
                <dt className="font-semibold text-bee-muted">Matched to</dt>
                <dd>{lookup.matched_provider}</dd>
              </div>
            </dl>
          )}
        </div>
      )}
    </div>
  );
}
