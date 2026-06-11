"use client";

import { useState } from "react";
import type { JourneyResponse } from "@/lib/types";

const TIER_LABEL: Record<string, string> = {
  high: "High confidence",
  medium: "Likely match",
  low: "Still narrowing it down",
};

export function LookupBanner({ data }: { data: JourneyResponse }) {
  const [expanded, setExpanded] = useState(false);
  const { screen, enrichment, context } = data;
  if (!screen.provider || screen.state !== "provider_identified") return null;

  const tier = screen.confidence_tier || context.lookup_confidence_tier;
  const employer = enrichment.lookup?.employer_query || context.employer_query;
  const lookup = enrichment.lookup;

  return (
    <div className="mb-5 rounded-card border-2 border-bee-yellow/40 bg-bee-yellow-tint p-5 lg:p-6">
      {tier && (
        <span className="mb-3 inline-block rounded-pill bg-bee-charcoal px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-white">
          {TIER_LABEL[tier] || tier}
        </span>
      )}

      <dl className="space-y-3">
        <div>
          <dt className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
            Matched provider
          </dt>
          <dd className="mt-1 text-xl font-extrabold tracking-[-0.02em] text-bee-charcoal">
            {screen.provider}
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
        {enrichment.check_destination && (
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
