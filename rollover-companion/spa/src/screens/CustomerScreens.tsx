import { BeeKeeperCard } from "../components/BeeKeeperCard";
import { BeeKeeperLink } from "../components/BeeKeeperLink";
import { FboSecurityCard } from "../components/FboSecurityCard";
import { MomentumRail } from "../components/MomentumRail";
import { PromoChip } from "../components/PromoChip";
import { TrustChip } from "../components/TrustChip";
import { WelcomeBack } from "../components/WelcomeBack";
import { getProvider, fboPayee, fullName, mailLine, totalSteps } from "../lib/journeyEngine";
import type { JourneyStore } from "../hooks/useJourney";
import type { Channel, ProviderMock, TaxType } from "../types/journey";

const STUCK_TIPS = [
  "The menu label might say Distributions instead of Rollover.",
  "Some portals hide rollover under Withdrawals.",
  "You may need to select Other or Not listed for the destination IRA.",
];

export function CustomerScreens({ store }: { store: JourneyStore }) {
  const { ctx, dispatch, dismissWelcome } = store;
  const provider = getProvider(ctx);
  const showRail = ctx.screen !== "find";

  return (
    <>
      {ctx.welcomeBack && <WelcomeBack onDismiss={dismissWelcome} />}
      {showRail && ctx.screen !== "complete" && <MomentumRail phase={ctx.phase} />}

      {ctx.screen === "find" && (
        <FindScreen
          onLookup={(e) => dispatch({ type: "lookup", employer: e })}
          onEscalate={() => dispatch({ type: "escalate" })}
        />
      )}

      {ctx.screen === "find_success" && (
        <div className="card">
          <h1 className="h1">Found it — your 401(k) is at {ctx.providerName}</h1>
          <p className="body-copy mt-3">Matched employer: {ctx.matchedEmployer}</p>
          <p className="mt-2 text-sm text-muted">
            The recordkeeper is the company that runs the plan day to day.
          </p>
          <button type="button" className="btn-primary mt-8" onClick={() => dispatch({ type: "continue" })}>
            Continue
          </button>
          <BeeKeeperLink onClick={() => dispatch({ type: "escalate" })} />
        </div>
      )}

      {ctx.screen === "find_disambiguate" && ctx.disambiguation && (
        <div className="card">
          <h1 className="h1">{ctx.disambiguation.question}</h1>
          <div className="mt-8 space-y-3">
            {ctx.disambiguation.options.map((opt) => (
              <button
                key={opt}
                type="button"
                className="btn-secondary"
                onClick={() => dispatch({ type: "disambiguate", answer: opt })}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      )}

      {ctx.screen === "find_not_covered" && (
        <div className="card">
          <h1 className="h1">Found it — it&apos;s at {ctx.providerName}</h1>
          <p className="body-copy mt-3">
            Your BeeKeeper will guide this one personally. Merrill plans need a concierge handoff —
            you&apos;re in good hands.
          </p>
          <BeeKeeperCard>
            Prefer a person? Your BeeKeeper can take it from here. They handle complex recordkeepers
            every day.
          </BeeKeeperCard>
          <button type="button" className="btn-primary mt-6" onClick={() => dispatch({ type: "escalate" })}>
            Connect me with my BeeKeeper
          </button>
        </div>
      )}

      {ctx.screen === "access" && (
        <div className="card">
          <h1 className="h1">Can you log in to {ctx.providerName}?</h1>
          <p className="body-copy mt-3">You&apos;ll need portal access to roll over online.</p>
          <div className="mt-8 space-y-3">
            <button type="button" className="btn-primary" onClick={() => dispatch({ type: "access", canLogin: true })}>
              Yes, I can log in
            </button>
            <button type="button" className="btn-secondary" onClick={() => dispatch({ type: "access", canLogin: false })}>
              No, not right now
            </button>
          </div>
          <BeeKeeperLink onClick={() => dispatch({ type: "escalate" })} />
        </div>
      )}

      {ctx.screen === "access_recovery" && (
        <div className="card">
          <h1 className="h1">Let&apos;s get you back in</h1>
          <p className="body-copy mt-3">Pick the path that fits — most people use one of these.</p>
          <div className="mt-6 space-y-3">
            <button type="button" className="btn-secondary" onClick={() => dispatch({ type: "recovery_path", path: "forgot" })}>
              Forgot password
            </button>
            <button type="button" className="btn-secondary" onClick={() => dispatch({ type: "recovery_path", path: "never" })}>
              Never logged in before
            </button>
          </div>
          <div className="mt-6 rounded-xl border border-border bg-canvas p-4 text-sm text-ink">
            <p className="font-semibold">Have ready</p>
            <ul className="mt-2 list-inside list-disc text-muted">
              <li>Last 4 of your SSN</li>
              <li>Date of birth</li>
              <li>Employment start/end dates (approximate is fine)</li>
            </ul>
          </div>
          <BeeKeeperCard>
            Access problems are frustrating — your BeeKeeper can reset credentials or walk you through
            first-time setup on a live call.
          </BeeKeeperCard>
          <button type="button" className="btn-primary mt-4" onClick={() => dispatch({ type: "escalate" })}>
            Talk to my BeeKeeper now
          </button>
        </div>
      )}

      {ctx.screen === "name" && <NameScreen onSubmit={(f, l) => dispatch({ type: "set_name", firstName: f, lastName: l })} onEscalate={() => dispatch({ type: "escalate" })} />}

      {ctx.screen === "tax" && (
        <TaxScreen
          onSelect={(t) => dispatch({ type: "set_tax", taxType: t })}
          onEscalate={() => dispatch({ type: "escalate" })}
        />
      )}

      {ctx.screen === "channel" && provider && (
        <ChannelScreen
          providerName={provider.name}
          onlineDays={provider.onlineDays}
          checkDays={provider.checkDays}
          onSelect={(c) => dispatch({ type: "set_channel", channel: c })}
          onEscalate={() => dispatch({ type: "escalate" })}
        />
      )}

      {ctx.screen === "channel_step" && provider && ctx.channel && (
        <ChannelStepScreen
          store={store}
          provider={provider}
          channel={ctx.channel}
          stepIndex={ctx.stepIndex}
          total={totalSteps(ctx)}
          payee={fboPayee(ctx)}
          mail={mailLine(ctx)}
          name={fullName(ctx)}
        />
      )}

      {ctx.screen === "stuck" && (
        <div className="card">
          <h1 className="h1">Let&apos;s get you unstuck</h1>
          <p className="body-copy mt-3">What usually trips people up here:</p>
          <ul className="mt-4 space-y-2 text-[17px] text-ink">
            {STUCK_TIPS.map((t) => (
              <li key={t} className="rounded-xl border border-border bg-canvas px-4 py-3">
                {t}
              </li>
            ))}
          </ul>
          <BeeKeeperCard>
            Prefer a person? Your BeeKeeper can take it from here — they know this portal inside out.
          </BeeKeeperCard>
          <button type="button" className="btn-primary mt-6" onClick={() => dispatch({ type: "step_done" })}>
            Try again
          </button>
          <button type="button" className="btn-secondary mt-3" onClick={() => dispatch({ type: "escalate" })}>
            Hand off to my BeeKeeper
          </button>
        </div>
      )}

      {ctx.screen === "escalated" && (
        <div className="card">
          <h1 className="h1">Your BeeKeeper is on it</h1>
          <p className="body-copy mt-3">
            A real person will pick up where you left off. You don&apos;t need to repeat yourself —
            we saved your progress.
          </p>
          <BeeKeeperCard>We&apos;ll reach out shortly to finish your rollover together.</BeeKeeperCard>
        </div>
      )}

      {ctx.screen === "track" && provider && (
        <div className="card">
          <h1 className="h1">Rollover initiated. You&apos;ve done the hard part.</h1>
          <p className="body-copy mt-3">
            {ctx.channel === "online" && provider.expressRollover
              ? `Fidelity Express rollovers often land in ${provider.onlineDays}.`
              : `Checks typically arrive in ${provider.checkDays}.`}
          </p>
          <FboSecurityCard payee={fboPayee(ctx)} mailTo={mailLine(ctx)} />
          <p className="text-sm text-muted">
            Nothing arrived after the window? Your BeeKeeper will chase it for you.
          </p>
          <button type="button" className="btn-primary mt-8" onClick={() => dispatch({ type: "track_continue" })}>
            Mark as complete
          </button>
          <BeeKeeperLink onClick={() => dispatch({ type: "escalate" })} />
        </div>
      )}

      {ctx.screen === "complete" && (
        <div className="card text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-bee text-2xl">✓</div>
          <h1 className="h1">One account, one place</h1>
          <p className="body-copy mt-3">Your old 401(k) is home. PensionBee adds 1% on eligible rollovers · terms apply.</p>
          <button type="button" className="btn-primary mt-8" onClick={() => store.restart()}>
            Start another rollover
          </button>
        </div>
      )}
    </>
  );
}

function FindScreen({ onLookup, onEscalate }: { onLookup: (e: string) => void; onEscalate: () => void }) {
  return (
    <div className="card">
      <h1 className="h1">Where did you work?</h1>
      <p className="body-copy mt-3">
        Enter your former employer or the company that runs your old 401(k).
      </p>
      <form
        className="mt-8"
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          const emp = String(fd.get("employer") || "").trim();
          if (emp) onLookup(emp);
        }}
      >
        <label className="block text-sm font-semibold text-ink" htmlFor="employer">
          Employer or provider
        </label>
        <input
          id="employer"
          name="employer"
          className="mt-2 w-full rounded-xl border border-border bg-white px-4 py-3.5 text-[17px] outline-none ring-ink focus:ring-2"
          placeholder="e.g. Amazon, Citi, Cardinal Micro"
          autoComplete="organization"
        />
        <button type="submit" className="btn-primary mt-6">
          Find my 401(k)
        </button>
      </form>
      <PromoChip />
      <BeeKeeperLink onClick={onEscalate} />
    </div>
  );
}

function NameScreen({
  onSubmit,
  onEscalate,
}: {
  onSubmit: (first: string, last: string) => void;
  onEscalate: () => void;
}) {
  return (
    <div className="card">
      <h1 className="h1">What name should checks use?</h1>
      <p className="body-copy mt-3">Checks get made out to you by name — we print it exactly.</p>
      <form
        className="mt-8"
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          onSubmit(String(fd.get("first")), String(fd.get("last")));
        }}
      >
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm font-semibold">First name</label>
            <input name="first" required className="mt-2 w-full rounded-xl border border-border px-4 py-3.5" defaultValue="Avery" />
          </div>
          <div>
            <label className="text-sm font-semibold">Last name</label>
            <input name="last" required className="mt-2 w-full rounded-xl border border-border px-4 py-3.5" defaultValue="Quinn" />
          </div>
        </div>
        <button type="submit" className="btn-primary mt-6">
          Continue
        </button>
      </form>
      <BeeKeeperLink onClick={onEscalate} />
    </div>
  );
}

function TaxScreen({ onSelect, onEscalate }: { onSelect: (t: TaxType) => void; onEscalate: () => void }) {
  const opts: { id: TaxType; label: string; hint: string }[] = [
    { id: "pre_tax", label: "Pre-tax (most common)", hint: "Goes to your Traditional IRA" },
    { id: "roth", label: "Roth", hint: "Goes to your Roth IRA" },
    { id: "both", label: "Both pre-tax and Roth", hint: "We'll split across IRA types" },
  ];
  return (
    <div className="card">
      <h1 className="h1">What type of money is in your old 401(k)?</h1>
      <div className="mt-8 space-y-3">
        {opts.map((o) => (
          <button key={o.id} type="button" className="btn-secondary" onClick={() => onSelect(o.id)}>
            {o.label}
            {"\n\n"}
            <span className="font-normal text-muted">{o.hint}</span>
          </button>
        ))}
      </div>
      <BeeKeeperLink onClick={onEscalate} />
    </div>
  );
}

function ChannelScreen({
  providerName,
  onlineDays,
  checkDays,
  onSelect,
  onEscalate,
}: {
  providerName: string;
  onlineDays: string;
  checkDays: string;
  onSelect: (c: Channel) => void;
  onEscalate: () => void;
}) {
  const fidelityNote = providerName === "Fidelity" ? `usually fastest — ${onlineDays} vs ${checkDays} by check` : onlineDays;
  return (
    <div className="card">
      <h1 className="h1">How do you want to start?</h1>
      <div className="mt-8 space-y-3">
        <button type="button" className="btn-primary" onClick={() => onSelect("online")}>
          Online portal
          {"\n\n"}
          <span className="font-normal opacity-90">{fidelityNote}</span>
        </button>
        <button type="button" className="btn-secondary" onClick={() => onSelect("phone")}>
          By phone
        </button>
        <button type="button" className="btn-secondary" onClick={() => onSelect("forms")}>
          I have paper forms
        </button>
      </div>
      <BeeKeeperCard>
        This step is easier with your BeeKeeper — they handle provider calls and paperwork every day.
      </BeeKeeperCard>
      <BeeKeeperLink onClick={onEscalate} />
    </div>
  );
}

function ChannelStepScreen({
  store,
  provider,
  channel,
  stepIndex,
  total,
  payee,
  mail,
  name,
}: {
  store: JourneyStore;
  provider: ProviderMock;
  channel: Channel;
  stepIndex: number;
  total: number;
  payee: string;
  mail: string;
  name: string;
}) {
  const { dispatch, ctx } = store;
  const showFbo = channel === "phone" || channel === "forms" || stepIndex >= total - 2;

  let stepText = "";
  if (channel === "online") stepText = provider.onlineSteps[stepIndex] ?? "";
  if (channel === "forms") stepText = provider.formSteps[stepIndex] ?? "";
  if (channel === "phone" && stepIndex === 0) stepText = provider.phoneScript.opening;

  const qa = channel === "phone" && stepIndex > 0 ? provider.phoneScript.qa[stepIndex - 1] : null;

  return (
    <div className="card">
      <p className="text-sm font-medium text-muted">
        Step {stepIndex + 1} of {total}
      </p>
      {ctx.reconstructed && stepIndex === 0 && (
        <div className="mt-3">
          <TrustChip />
        </div>
      )}
      {provider.phoneVerificationNote && stepIndex === 0 && channel === "online" && (
        <p className="mt-3 text-sm text-muted">{provider.phoneVerificationNote}</p>
      )}
      {provider.notaryEdgeCase && stepIndex === 0 && (
        <p className="mt-3 rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-900">{provider.notaryEdgeCase}</p>
      )}

      {channel === "phone" && stepIndex === 0 ? (
        <>
          <h1 className="h1 mt-4">Your opening line</h1>
          <blockquote className="mt-4 border-l-4 border-bee pl-4 text-[17px] font-medium leading-relaxed text-ink">
            &ldquo;{provider.phoneScript.opening.replace("[your name]", name)}&rdquo;
          </blockquote>
        </>
      ) : qa ? (
        <>
          <h1 className="h1 mt-4">Read-along</h1>
          <div className="mt-4 rounded-xl border border-border bg-canvas p-4">
            <p className="text-xs font-bold uppercase tracking-wider text-muted">They ask</p>
            <p className="mt-1 font-semibold text-ink">{qa.theyAsk}</p>
            <p className="mt-4 text-xs font-bold uppercase tracking-wider text-muted">You say</p>
            <p className="mt-1 text-[17px] text-ink">{qa.youSay.replace("[your name]", name)}</p>
          </div>
        </>
      ) : (
        <>
          <h1 className="h1 mt-4">Do this now</h1>
          <p className="body-copy mt-4">{stepText.replace(/\[your name\]/g, name)}</p>
        </>
      )}

      {showFbo && <FboSecurityCard payee={payee} mailTo={mail} />}

      <button type="button" className="btn-primary mt-6" onClick={() => dispatch({ type: "step_done" })}>
        Done — next
      </button>
      <button type="button" className="btn-secondary mt-3" onClick={() => dispatch({ type: "step_stuck" })}>
        I&apos;m stuck
      </button>
      <BeeKeeperLink onClick={() => dispatch({ type: "escalate" })} />
    </div>
  );
}
