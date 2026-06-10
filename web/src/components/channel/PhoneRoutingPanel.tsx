import type { ChannelContext, ScreenEnrichment } from "@/lib/types";
import type { ChannelSurface } from "../ChannelWalkthrough";
import { AgentCustodianNote } from "./AgentCustodianNote";
import { RoutingSecurityCard } from "./RoutingSecurityCard";

/**
 * Step 5+ phone routing block — compound security card for payee + mail.
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

  if (!payable && !mail) return null;

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

      <RoutingSecurityCard payeeLine={payable || undefined} mailingAddress={mail || undefined} />

      {surface === "agent" && <AgentCustodianNote enrichment={enrichment} />}
    </div>
  );
}
