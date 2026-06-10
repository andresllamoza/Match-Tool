import type { ChannelContext, ScreenEnrichment } from "@/lib/types";
import { isFboPayableLine } from "@/lib/checkPayable";
import type { ChannelSurface } from "../ChannelWalkthrough";
import { AgentCustodianNote } from "./AgentCustodianNote";
import { FboSecurityCard } from "./FboSecurityCard";
import { FinancialCopyField } from "./FinancialCopyField";

/**
 * Step 5+ phone routing block — FBO guardrail first, then mailing utilities.
 */
export function PhoneRoutingPanel({
  ctx,
  enrichment,
  surface,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
  surface: ChannelSurface;
}) {
  const payable = ctx.check_payable ?? "";
  const mail = ctx.mailing_address || enrichment.mailing_address;
  const showFbo = payable && isFboPayableLine(payable);

  if (!showFbo && !mail && !payable) return null;

  return (
    <div className="space-y-6 border-t border-[#EAE5DC] pt-8">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          Check routing
        </p>
        <p className="mt-1 text-sm leading-relaxed text-[#1E242B]">
          When the rep asks how to make the check payable, use the exact payee line
          below — then confirm where they will mail it.
        </p>
      </div>

      {showFbo && <FboSecurityCard payableLine={payable} />}

      {surface === "agent" && <AgentCustodianNote enrichment={enrichment} />}

      <div className="grid gap-4 sm:grid-cols-2">
        {!showFbo && payable && (
          <FinancialCopyField label="Payee name" value={payable} />
        )}
        {mail && <FinancialCopyField label="Mailing address" value={mail} />}
      </div>
    </div>
  );
}
