import type { ChannelContext, ScreenEnrichment } from "@/lib/types";
import { CopyChip } from "./CopyChip";

export function ChannelWalkthrough({ enrichment }: { enrichment: ScreenEnrichment }) {
  const ctx = enrichment.channel_context;
  if (!ctx) return null;

  if (ctx.channel === "phone") {
    return <PhoneWalkthrough ctx={ctx} enrichment={enrichment} />;
  }
  if (ctx.channel === "forms") {
    return <FormsWalkthrough ctx={ctx} enrichment={enrichment} />;
  }
  return <OnlineWalkthrough ctx={ctx} enrichment={enrichment} />;
}

function PhoneWalkthrough({
  ctx,
  enrichment,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
}) {
  return (
    <div className="mb-5 space-y-3">
      {ctx.phone && (
        <a
          href={`tel:${ctx.phone.replace(/[^\d+]/g, "")}`}
          className="flex items-center justify-between rounded-card bg-bee-blue px-5 py-4 text-white shadow-sm transition-transform hover:scale-[1.01] active:scale-[0.99]"
        >
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-white/80">Tap to call</p>
            <p className="text-xl font-bold">{ctx.phone}</p>
          </div>
          <span className="text-2xl" aria-hidden>
            📞
          </span>
        </a>
      )}

      {ctx.intro && ctx.step_label === "Step 1" && (
        <div className="rounded-card bg-cream px-4 py-3 text-sm text-bee-ink lg:text-base">
          <p className="text-xs font-bold uppercase text-bee-muted">Opening line</p>
          <p className="mt-1 font-medium">{ctx.intro}</p>
        </div>
      )}

      <div className="rounded-card border-2 border-bee-blue/20 bg-white p-5 lg:p-6">
        <p className="text-xs font-bold uppercase tracking-wide text-bee-blue">Say this</p>
        <p className="mt-2 text-lg font-semibold leading-relaxed text-bee-ink lg:text-xl">
          &ldquo;{ctx.say_this}&rdquo;
        </p>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {ctx.check_payable && <CopyChip label="Check payable to" value={ctx.check_payable} />}
        {ctx.mailing_address && <CopyChip label="Mailing address" value={ctx.mailing_address} />}
      </div>

      {ctx.rep_questions.length > 0 && (
        <div className="rounded-card bg-bee-blue-light/50 p-4 lg:p-5">
          <p className="mb-3 text-sm font-bold text-bee-blue">If the rep asks…</p>
          <dl className="space-y-3">
            {ctx.rep_questions.map((q, i) => (
              <div key={i} className="rounded-card bg-white/80 px-4 py-3">
                <dt className="font-semibold text-bee-ink">{q.question}</dt>
                <dd className="mt-1 text-sm text-bee-muted lg:text-base">{q.answer}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {enrichment.forward_step_required && (
        <p className="rounded-card border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          This provider mails the check to you first — PensionBee will send a prepaid envelope to
          forward it.
        </p>
      )}
    </div>
  );
}

function OnlineWalkthrough({
  ctx,
  enrichment,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
}) {
  return (
    <div className="mb-5 space-y-3">
      {enrichment.general_path && (
        <p className="rounded-card bg-bee-blue-light/50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-bee-blue">
          General rollover guide — look for Withdrawals / Rollovers in your provider portal
        </p>
      )}

      <div className="rounded-card border-2 border-bee-blue/20 bg-white p-5 lg:p-6">
        <p className="text-xs font-bold uppercase tracking-wide text-bee-blue">Do this now</p>
        <p className="mt-2 text-lg font-semibold leading-relaxed text-bee-ink lg:text-xl">
          {ctx.say_this}
        </p>
      </div>

      {ctx.portal_menu_hints && ctx.portal_menu_hints.length > 0 && (
        <div className="rounded-card bg-cream px-4 py-3">
          <p className="text-xs font-bold uppercase text-bee-muted">Look for these menu labels</p>
          <p className="mt-1 text-sm text-bee-ink lg:text-base">
            {ctx.portal_menu_hints.join(" · ")}
          </p>
        </div>
      )}

      {ctx.destination_hints && ctx.destination_hints.length > 0 && (
        <div className="rounded-card bg-cream px-4 py-3">
          <p className="text-xs font-bold uppercase text-bee-muted">Destination dropdown options</p>
          <p className="mt-1 text-sm text-bee-ink lg:text-base">
            {ctx.destination_hints.join(" · ")}
          </p>
        </div>
      )}

      <div className="grid gap-2 sm:grid-cols-2">
        <CopyChip label="Destination" value={enrichment.destination_name} />
        {ctx.check_payable && <CopyChip label="Check payable to" value={ctx.check_payable} />}
        <CopyChip label="Mailing address" value={enrichment.mailing_address} />
      </div>
      {enrichment.forward_step_required && (
        <p className="rounded-card border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Expect the check at your home address — not PensionBee directly.
        </p>
      )}
    </div>
  );
}

function FormsWalkthrough({
  ctx,
  enrichment,
}: {
  ctx: ChannelContext;
  enrichment: ScreenEnrichment;
}) {
  return (
    <div className="mb-5 space-y-3">
      <div className="rounded-card border-2 border-dashed border-bee-blue/30 bg-white p-5 lg:p-6">
        <p className="text-xs font-bold uppercase text-bee-muted">Form field</p>
        <p className="mt-1 text-lg font-bold text-bee-blue">{ctx.form_field_label}</p>
        <p className="mt-3 text-base leading-relaxed text-bee-ink lg:text-lg">{ctx.say_this}</p>
      </div>
      <div className="grid gap-2">
        <CopyChip label="Receiving provider" value={enrichment.destination_name} />
        <CopyChip label="Mailing address" value={enrichment.mailing_address} />
        {ctx.check_payable && <CopyChip label="Check payable to" value={ctx.check_payable} />}
      </div>
    </div>
  );
}
