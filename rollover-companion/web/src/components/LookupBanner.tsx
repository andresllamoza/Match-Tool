import type { JourneyResponse } from "@/lib/types";

const TIER_LABEL: Record<string, string> = {
  high: "High confidence match",
  medium: "Likely match",
  low: "Still narrowing it down",
};

export function LookupBanner({ data }: { data: JourneyResponse }) {
  const { screen, enrichment, context } = data;
  if (!screen.provider || screen.state !== "provider_identified") return null;

  const tier = screen.confidence_tier || context.lookup_confidence_tier;
  const employer = enrichment.lookup?.employer_query || context.employer_query;

  return (
    <div className="mb-5 rounded-card border-2 border-bee-blue/15 bg-bee-blue-light/40 p-5 lg:p-6">
      {tier && (
        <span className="mb-2 inline-block rounded-pill bg-bee-blue px-2.5 py-0.5 text-xs font-bold text-white">
          {TIER_LABEL[tier] || tier}
        </span>
      )}
      <p className="text-lg font-bold text-bee-blue lg:text-xl">
        Your 401(k) is most likely with {screen.provider}
      </p>
      {employer && (
        <p className="mt-1 text-sm text-bee-muted lg:text-base">
          Based on public plan filings for {employer}.
        </p>
      )}
      {enrichment.check_destination && (
        <p className="mt-3 text-sm text-bee-ink lg:text-base">
          <span className="font-semibold">Check path:</span> {enrichment.check_destination}
        </p>
      )}
    </div>
  );
}
