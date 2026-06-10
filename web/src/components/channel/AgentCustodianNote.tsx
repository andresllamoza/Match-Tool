import type { ScreenEnrichment } from "@/lib/types";

export function AgentCustodianNote({
  enrichment,
}: {
  enrichment: ScreenEnrichment;
}) {
  if (!enrichment.check_destination) return null;

  const directToCustodian = !enrichment.forward_step_required;
  const mechanism = enrichment.mechanism ?? "unknown";

  return (
    <div className="rounded-2xl border border-dashed border-[#6B6560]/35 bg-[#FAF8F5] px-6 py-5 text-sm leading-relaxed text-[#555555] sm:px-8">
      <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
        BeeKeeper — routing rationale
      </p>
      <p className="mt-2 text-[#1E242B]">
        <span className="font-semibold">{enrichment.check_destination}</span>
        {directToCustodian ? (
          <>
            {" "}
            — this provider supports direct-to-custodian mailing. Do not coach
            participant forwarding unless the rep insists on mailing to the
            member first.
          </>
        ) : (
          <>
            {" "}
            — participant-forward pattern required ({mechanism.replace(/_/g, " ")}
            ). Pre-empt with prepaid envelope expectations before the user
            initiates.
          </>
        )}
      </p>
    </div>
  );
}
