import type { JourneyPhase } from "@/lib/types";

const TIPS: Record<JourneyPhase, string[]> = {
  find: [
    "Your former employer isn't the recordkeeper — Fidelity, Vanguard, etc. hold the money.",
    "A recent pay stub or W-2 often shows who manages your 401(k).",
  ],
  access: [
    "Use 'Forgot password' before calling — it's usually faster.",
    "Have your SSN and date of birth ready for identity verification.",
  ],
  rollover: [
    "Pre-tax → Traditional IRA. Roth → Roth IRA. Never mix without help.",
    "Capture every confirmation screen — it helps if something stalls.",
  ],
  track: [
    "Most rollovers take 2–4 weeks. Voya can be slower.",
    "If nothing arrives by the expected date, a BeeKeeper can trace it.",
  ],
};

export function CustomerHelpPanel({ phase }: { phase: JourneyPhase }) {
  return (
    <aside className="hidden lg:block">
      <div className="sticky top-8 space-y-4">
        <div className="pb-card p-6">
          <h2 className="mb-3 text-sm font-bold uppercase tracking-wide text-bee-charcoal">
            Good to know
          </h2>
          <ul className="space-y-3 text-sm leading-relaxed text-bee-ink">
            {TIPS[phase].map((tip, i) => (
              <li key={i} className="flex gap-2">
                <span className="mt-0.5 text-bee-yellow">●</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-card border-2 border-bee-yellow bg-bee-yellow-soft p-6">
          <p className="font-bold text-bee-charcoal">Real humans, real help</p>
          <p className="mt-2 text-sm text-bee-ink">
            Your BeeKeeper is available on phone, chat, and email — Mon–Fri 9:30am–5pm ET.
          </p>
        </div>
      </div>
    </aside>
  );
}
