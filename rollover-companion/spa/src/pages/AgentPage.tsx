import { Link } from "react-router-dom";
import { MomentumRail } from "../components/MomentumRail";
import { useJourneyContext } from "../context/JourneyProvider";
import { fboPayee, fullName, getProvider, mailLine } from "../lib/journeyEngine";
import { CustomerScreens } from "../screens/CustomerScreens";

export function AgentPage() {
  const store = useJourneyContext();
  const { ctx } = store;
  const provider = getProvider(ctx);

  const sayNext =
    ctx.screen === "channel_step" && provider && ctx.channel === "phone"
      ? provider.phoneScript.opening
      : ctx.screen === "find_not_covered"
        ? `I see your 401(k) is at ${ctx.providerName}. I'll guide this rollover personally — let's start with confirming your employer name.`
        : `You're on ${ctx.screen.replace(/_/g, " ")}. Confirm the customer can see their current step.`;

  return (
    <div className="min-h-dvh bg-canvas">
      <header className="border-b border-border bg-white px-6 py-4">
        <div className="mx-auto flex max-w-[1100px] items-center justify-between">
          <div>
            <p className="text-lg font-bold text-ink">BeeKeeper console</p>
            <p className="text-sm text-muted">Live journey mirror</p>
          </div>
          <Link to="/" className="text-sm font-semibold text-muted hover:text-ink">
            ← Customer app
          </Link>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1100px] gap-8 px-6 py-8 lg:grid-cols-2">
        <section>
          <p className="mb-4 text-xs font-bold uppercase tracking-wider text-muted">Customer preview (read-only)</p>
          <div className="pointer-events-none opacity-95">
            <CustomerScreens store={store} />
          </div>
        </section>

        <aside className="rounded-2xl bg-ink p-6 text-white lg:sticky lg:top-8 lg:self-start">
          <MomentumRail phase={ctx.phase} />

          <section className="mb-6">
            <h2 className="text-xs font-bold uppercase tracking-wider text-bee">Say next</h2>
            <p className="mt-2 text-[17px] leading-relaxed">{sayNext}</p>
          </section>

          <section className="mb-6 border-t border-white/10 pt-6">
            <h2 className="text-xs font-bold uppercase tracking-wider text-bee">Agent notes</h2>
            <ul className="mt-2 space-y-2 text-sm text-white/85">
              {provider?.notaryEdgeCase && <li>· Notary edge case possible</li>}
              {provider?.mailToUser && <li>· Check mails to participant first — prepaid envelope</li>}
              {provider?.phoneVerificationNote && <li>· {provider.phoneVerificationNote}</li>}
              <li>· FBO line: {fboPayee(ctx)}</li>
              <li>· Mail: {mailLine(ctx)}</li>
            </ul>
          </section>

          <section className="mb-6 border-t border-white/10 pt-6">
            <h2 className="text-xs font-bold uppercase tracking-wider text-bee">Active escalations</h2>
            <p className="mt-2 text-sm text-white/85">
              {ctx.escalated || ctx.screen === "stuck" ? "Customer may need handoff" : "None"}
            </p>
          </section>

          <section className="mb-6 border-t border-white/10 pt-6">
            <h2 className="text-xs font-bold uppercase tracking-wider text-bee">Edge cases</h2>
            <p className="mt-2 text-sm text-white/85">
              {provider?.notaryEdgeCase || "Standard path"}
            </p>
          </section>

          <p className="border-t border-white/10 pt-4 font-mono text-xs text-white/50">
            state={ctx.screen} · provider={ctx.providerId ?? "—"} · channel={ctx.channel ?? "—"} ·
            step={ctx.stepIndex} · customer={fullName(ctx)}
          </p>
        </aside>
      </main>
    </div>
  );
}
