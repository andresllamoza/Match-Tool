import type { ChannelContext, ScreenEnrichment } from "@/lib/types";
import { isFboPayableLine, showMailingDetails } from "@/lib/checkPayable";
import { AgentCustodianNote } from "./channel/AgentCustodianNote";
import { CallScriptCard } from "./channel/CallScriptCard";
import { FboSecurityCard } from "./channel/FboSecurityCard";
import { FinancialCopyField } from "./channel/FinancialCopyField";

export type ChannelSurface = "customer" | "agent" | "embed";

export function ChannelWalkthrough({
  enrichment,
  stepIndex = 0,
  totalSteps = 0,
  surface = "customer",
}: {
  enrichment: ScreenEnrichment;
  stepIndex?: number;
  totalSteps?: number;
  surface?: ChannelSurface;
}) {
  const ctx = enrichment.channel_context;
  if (!ctx) return null;

  if (ctx.channel === "phone") {
    return (
      <PhoneWalkthrough
        ctx={ctx}
        enrichment={enrichment}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        surface={surface}
      />
    );
  }
  if (ctx.channel === "forms") {
    return (
      <FormsWalkthrough
        ctx={ctx}
        enrichment={enrichment}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        surface={surface}
      />
    );
  }
  return (
    <OnlineWalkthrough
      ctx={ctx}
      enrichment={enrichment}
      stepIndex={stepIndex}
      totalSteps={totalSteps}
      surface={surface}
    />
  );
}

function MailingBlock({
  ctx,
  enrichment,
  stepIndex,
  totalSteps,
  surface,
  includeDestination = false,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
  stepIndex: number;
  totalSteps: number;
  surface: ChannelSurface;
  includeDestination?: boolean;
}) {
  if (!showMailingDetails(ctx.say_this, stepIndex, totalSteps)) return null;

  const payable = ctx.check_payable ?? "";
  const mail = ctx.mailing_address || enrichment.mailing_address;
  const showFbo = payable && isFboPayableLine(payable);
  const showPayableField = payable && !showFbo;

  return (
    <div className="space-y-3">
      {showFbo && <FboSecurityCard payableLine={payable} />}

      {surface === "agent" && <AgentCustodianNote enrichment={enrichment} />}

      <div className="grid gap-2 sm:grid-cols-2">
        {includeDestination && (
          <FinancialCopyField label="Destination" value={enrichment.destination_name} />
        )}
        {showPayableField && (
          <FinancialCopyField label="Payee name" value={payable} />
        )}
        {mail && <FinancialCopyField label="Mailing address" value={mail} />}
      </div>
    </div>
  );
}

function PhoneWalkthrough({
  ctx,
  enrichment,
  stepIndex,
  totalSteps,
  surface,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
  stepIndex: number;
  totalSteps: number;
  surface: ChannelSurface;
}) {
  return (
    <div className="mb-5 space-y-3">
      {ctx.phone && (
        <a
          href={`tel:${ctx.phone.replace(/[^\d+]/g, "")}`}
          className="flex items-center justify-between rounded-2xl bg-[#111111] px-5 py-4 text-white shadow-sm transition-all hover:bg-[#1E242B] active:scale-[0.98]"
        >
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-white/80">
              Tap to call
            </p>
            <p className="text-xl font-bold">{ctx.phone}</p>
          </div>
          <span className="text-2xl" aria-hidden>
            📞
          </span>
        </a>
      )}

      {ctx.intro && ctx.step_label === "Step 1" && (
        <div className="rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] px-4 py-3 text-sm text-[#1E242B]">
          <p className="text-xs font-bold uppercase text-[#6B6560]">Opening line</p>
          <p className="mt-1 font-medium">{ctx.intro}</p>
        </div>
      )}

      <CallScriptCard channel="phone" script={ctx.say_this} surface={surface} />

      <MailingBlock
        ctx={ctx}
        enrichment={enrichment}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        surface={surface}
      />

      {ctx.rep_questions.length > 0 && (
        <div className="rounded-xl border border-[#EAE5DC] bg-[#FFF9E6]/60 p-4 lg:p-5">
          <p className="mb-3 text-sm font-bold text-[#111111]">If the rep asks…</p>
          <dl className="space-y-3">
            {ctx.rep_questions.map((q, i) => (
              <div
                key={i}
                className="rounded-xl border border-[#EAE5DC] bg-white px-4 py-3"
              >
                <dt className="font-semibold text-[#1E242B]">{q.question}</dt>
                <dd className="mt-1 text-sm text-[#6B6560] lg:text-base">{q.answer}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {enrichment.forward_step_required && (
        <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          This provider mails the check to you first — PensionBee will send a prepaid
          envelope to forward it.
        </p>
      )}
    </div>
  );
}

function OnlineWalkthrough({
  ctx,
  enrichment,
  stepIndex,
  totalSteps,
  surface,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
  stepIndex: number;
  totalSteps: number;
  surface: ChannelSurface;
}) {
  return (
    <div className="mb-5 space-y-3">
      {enrichment.general_path && (
        <p className="rounded-xl border border-[#FFC72C]/40 bg-[#FFF9E6] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[#111111]">
          General rollover guide — look for Withdrawals / Rollovers in your provider
          portal
        </p>
      )}

      <CallScriptCard channel="online" script={ctx.say_this} surface={surface} />

      {ctx.portal_menu_hints && ctx.portal_menu_hints.length > 0 && (
        <div className="rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] px-4 py-3">
          <p className="text-xs font-bold uppercase text-[#6B6560]">
            Look for these menu labels
          </p>
          <p className="mt-1 text-sm text-[#1E242B] lg:text-base">
            {ctx.portal_menu_hints.join(" · ")}
          </p>
        </div>
      )}

      {ctx.destination_hints && ctx.destination_hints.length > 0 && (
        <div className="rounded-xl border border-[#EAE5DC] bg-[#FAF8F5] px-4 py-3">
          <p className="text-xs font-bold uppercase text-[#6B6560]">
            Destination dropdown options
          </p>
          <p className="mt-1 text-sm text-[#1E242B] lg:text-base">
            {ctx.destination_hints.join(" · ")}
          </p>
        </div>
      )}

      <MailingBlock
        ctx={ctx}
        enrichment={enrichment}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        surface={surface}
        includeDestination
      />

      {enrichment.forward_step_required && (
        <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Expect the check at your home address — not PensionBee directly.
        </p>
      )}
    </div>
  );
}

function FormsWalkthrough({
  ctx,
  enrichment,
  stepIndex,
  totalSteps,
  surface,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
  stepIndex: number;
  totalSteps: number;
  surface: ChannelSurface;
}) {
  return (
    <div className="mb-5 space-y-3">
      <CallScriptCard
        channel="forms"
        script={ctx.say_this}
        fieldLabel={ctx.form_field_label}
        surface={surface}
      />

      <MailingBlock
        ctx={ctx}
        enrichment={enrichment}
        stepIndex={stepIndex}
        totalSteps={totalSteps}
        surface={surface}
        includeDestination
      />
    </div>
  );
}
