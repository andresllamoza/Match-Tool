"use client";

import { deriveSourceStatus } from "@/lib/sourceStatus";
import type { JourneyController } from "@/hooks/useJourneyController";
import { useJourneyController } from "@/hooks/useJourneyController";
import type { JourneyResponse } from "@/lib/types";
import { AgentPanel } from "./AgentPanel";
import { AssistantDrawer } from "./AssistantDrawer";
import { ChannelWalkthrough, type ChannelSurface } from "./ChannelWalkthrough";
import { ChannelStepHeader } from "./channel/ChannelStepHeader";
import { EdgeCaseAlerts } from "./EdgeCaseAlerts";
import { FindEmployerStep } from "./FindEmployerStep";
import { LookupBanner } from "./LookupBanner";
import { ProgressSteps } from "./ProgressSteps";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { TrackPanel } from "./TrackPanel";
import { Button } from "./ui/Button";
import { SelectionBlock } from "./ui/SelectionBlock";
import { SourceStatusBadge } from "./ui/SourceStatusBadge";
import { StepTransition } from "./ui/StepTransition";

interface JourneyFlowProps {
  mode?: "customer" | "agent" | "embed";
  theme?: "default" | "minimal" | "dark";
  surface?: "default" | "sandbox";
  initialEmployer?: string;
  onPhaseChange?: (phase: import("@/lib/types").JourneyPhase) => void;
  controller?: JourneyController;
  readOnly?: boolean;
  hideAssistant?: boolean;
  channelSurface?: ChannelSurface;
}

type DecisionMode =
  | "tax"
  | "employer"
  | "provider_pick"
  | "disambiguation"
  | "access"
  | "channel"
  | "channel_step"
  | "track"
  | "stuck"
  | "confirm"
  | "done";

function resolveDecisionMode(
  data: JourneyResponse,
  showProviderPicker: boolean
): DecisionMode {
  const { screen, enrichment } = data;
  const inChannel = ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(
    screen.state
  );

  if (screen.state === "complete" || screen.state === "escalated") return "done";
  if (enrichment.requires_tax_selection) return "tax";
  if (showProviderPicker) return "provider_pick";
  if (screen.disambiguation_question && screen.disambiguation_options.length > 0) {
    return "disambiguation";
  }
  if (screen.state === "provider_unknown") return "employer";
  if (screen.state === "provider_identified" || screen.state === "provider_not_covered") {
    return "access";
  }
  if (
    screen.state === "access_recovered" &&
    screen.secondary_actions.some((a) => /phone|form/i.test(a))
  ) {
    return "channel";
  }
  if (inChannel) return "channel_step";
  if (screen.state === "stuck") return "stuck";
  if (screen.state === "initiated" || screen.state === "in_flight") return "track";
  if (screen.state === "access_blocked" || screen.state === "access_recovered") return "confirm";
  return "confirm";
}

export function JourneyFlow({
  mode = "customer",
  theme = "default",
  surface = "default",
  initialEmployer = "",
  onPhaseChange,
  controller: externalController,
  readOnly = false,
  hideAssistant = false,
  channelSurface: channelSurfaceOverride,
}: JourneyFlowProps) {
  const isSandbox = surface === "sandbox";
  const isAgent = mode === "agent";
  const internalController = useJourneyController({
    withAgentIntel: isAgent,
    initialEmployer,
    onPhaseChange,
    autoStart: !externalController,
  });
  const {
    data,
    loading,
    error,
    employerInput,
    setEmployerInput,
    showProviderPicker,
    setShowProviderPicker,
    providers,
    assistantOpen,
    setAssistantOpen,
    act,
    setError,
  } = externalController ?? internalController;

  const disabled = loading || readOnly;

  if (loading && !data) {
    return (
      <div className="flex min-h-[50dvh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-yellow/30 border-t-bee-yellow" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="pb-card p-6 text-center text-red-800">
        {error || "Unable to start journey."}
      </div>
    );
  }

  const { screen, context, step_index, total_steps, enrichment } = data;
  const showProgress = screen.state !== "complete" && screen.state !== "escalated";
  const inChannel = ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(
    screen.state
  );
  const decision = resolveDecisionMode(data, showProviderPicker);
  const sourceStatus = deriveSourceStatus(screen);
  const channelSurface: ChannelSurface =
    channelSurfaceOverride ??
    (mode === "agent" ? "agent" : mode === "embed" ? "embed" : "customer");
  const channelLabel =
    screen.channel === "online"
      ? "online"
      : screen.channel === "phone"
        ? "by phone"
        : screen.channel === "forms"
          ? "paper forms"
          : "";

  async function handlePrimary() {
    const s = screen.state;
    const primary = screen.primary_action.toLowerCase();

    if (s === "provider_unknown") {
      const name = employerInput.trim();
      if (!name) {
        setError("Enter your former employer to continue.");
        return;
      }
      await act({ type: "lookup", employer: name });
      return;
    }
    if (s === "access_blocked" && primary.includes("in now")) {
      await act({ type: "access_recovered" });
      return;
    }
    if (inChannel && primary.includes("done")) {
      await act({ type: "step", outcome: "done" });
      return;
    }
    if (s === "initiated") {
      await act({ type: "confirm_in_flight" });
      return;
    }
    if (s === "in_flight" && primary.includes("complete")) {
      await act({ type: "mark_complete" });
      return;
    }
    if (s === "stuck" && primary.includes("beekeeper")) {
      await act({ type: "escalate", reason: "stuck_on_step" });
      return;
    }
    if (s === "access_recovered" && primary.includes("online")) {
      await act({ type: "channel", channel: "online" });
    }
  }

  async function handleTaxPick(taxType: string) {
    await act({ type: "tax_type", tax_type: taxType });
  }

  async function handleAccess(canLogin: boolean) {
    await act({ type: "access", can_login: canLogin });
  }

  async function handleChannel(channel: "online" | "phone" | "forms") {
    await act({ type: "channel", channel });
  }

  async function handleDisambiguation(option: string) {
    await act({ type: "disambiguate", answer: option });
  }

  async function handleProviderPick(provider: string) {
    setShowProviderPicker(false);
    await act({ type: "provider_direct", provider });
  }

  async function handleEscalate(reason: string) {
    await act({ type: "escalate", reason });
  }

  async function handleHandoff() {
    await act({ type: "handoff", reason: "provider_not_covered" });
  }

  function renderDecision() {
    if (decision === "done") return null;

    if (decision === "tax") {
      const options =
        enrichment.tax_options.length > 0
          ? enrichment.tax_options
          : [
              { id: "pre_tax", label: "Pre-tax (Traditional IRA)", hint: "Most common 401(k) balance" },
              { id: "roth", label: "Roth (Roth IRA)", hint: "After-tax contributions and earnings" },
              { id: "both", label: "Both pre-tax and Roth", hint: "Split across two IRA types" },
            ];
      return (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-bee-charcoal lg:text-base">
            How is your old 401(k) taxed?
          </p>
          {options.map((opt) => (
            <SelectionBlock
              key={opt.id}
              label={opt.label}
              description={opt.hint}
              onClick={() => handleTaxPick(opt.id)}
              disabled={disabled}
            />
          ))}
        </div>
      );
    }

    if (decision === "provider_pick") {
      return (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-bee-charcoal lg:text-base">
            Select your 401(k) provider
          </p>
          {providers.map((p) => (
            <SelectionBlock
              key={p}
              label={p}
              onClick={() => handleProviderPick(p)}
              disabled={disabled}
            />
          ))}
          <button
            type="button"
            onClick={() => setShowProviderPicker(false)}
            className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
          >
            ← Search by employer instead
          </button>
        </div>
      );
    }

    if (decision === "disambiguation") {
      return (
        <div className="space-y-3">
          <p className="text-base font-semibold text-bee-charcoal lg:text-lg">
            {screen.disambiguation_question}
          </p>
          {screen.disambiguation_options.map((opt) => (
            <SelectionBlock
              key={opt}
              label={opt}
              onClick={() => handleDisambiguation(opt)}
              disabled={disabled}
            />
          ))}
        </div>
      );
    }

    if (decision === "access") {
      return (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-bee-charcoal lg:text-base">
            Can you log in to your old 401(k) account right now?
          </p>
          <SelectionBlock
            label="Yes, I can log in"
            description="We'll walk you through the rollover in your provider portal or by phone."
            onClick={() => handleAccess(true)}
            disabled={disabled}
          />
          <SelectionBlock
            label="No, I'm locked out or never had access"
            description="We'll help you recover access or connect you with a BeeKeeper."
            onClick={() => handleAccess(false)}
            disabled={disabled}
          />
          {screen.state === "provider_not_covered" && (
            <button
              type="button"
              onClick={handleHandoff}
              disabled={disabled}
              className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
            >
              Talk to a BeeKeeper about this provider →
            </button>
          )}
        </div>
      );
    }

    if (decision === "channel") {
      return (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-bee-charcoal lg:text-base">
            How would you like to start your rollover?
          </p>
          <SelectionBlock
            label="Online"
            description="Fastest when you can log in to your provider's website."
            onClick={() => handleChannel("online")}
            disabled={disabled}
          />
          <SelectionBlock
            label="By phone"
            description="We'll give you the number and exactly what to say."
            onClick={() => handleChannel("phone")}
            disabled={disabled}
          />
          <SelectionBlock
            label="Paper forms"
            description="Download, fill out, and mail a distribution form."
            onClick={() => handleChannel("forms")}
            disabled={disabled}
          />
        </div>
      );
    }

    if (decision === "channel_step") {
      return (
        <div className="space-y-3">
          <Button onClick={handlePrimary} disabled={disabled}>
            {screen.primary_action}
          </Button>
          <button
            type="button"
            onClick={() => act({ type: "step", outcome: "stuck" })}
            disabled={disabled}
            className="w-full py-2 text-center text-sm font-semibold text-red-700 hover:underline"
          >
            I&apos;m stuck on this step
          </button>
        </div>
      );
    }

    if (decision === "stuck") {
      return (
        <div className="space-y-3">
          <Button onClick={handlePrimary} disabled={disabled}>
            {screen.primary_action}
          </Button>
          <button
            type="button"
            onClick={() => act({ type: "resume" })}
            disabled={disabled}
            className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
          >
            Try this step again →
          </button>
        </div>
      );
    }

    if (decision === "track") {
      return (
        <div className="space-y-3">
          <Button onClick={handlePrimary} disabled={disabled}>
            {screen.primary_action}
          </Button>
          {screen.secondary_actions.map((action) => {
            const lower = action.toLowerCase();
            if (lower.includes("nothing arrived") || lower.includes("get help")) {
              return (
                <button
                  key={action}
                  type="button"
                  onClick={() => handleEscalate("tracking_delay")}
                  disabled={disabled}
                  className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
                >
                  {action} →
                </button>
              );
            }
            return null;
          })}
        </div>
      );
    }

    return (
      <div className="space-y-3">
        <Button onClick={handlePrimary} disabled={disabled}>
          {screen.primary_action}
        </Button>
        {screen.state === "access_blocked" &&
          screen.secondary_actions.map((action) => {
            const lower = action.toLowerCase();
            if (lower.includes("locked out") || lower.includes("beekeeper")) {
              return (
                <button
                  key={action}
                  type="button"
                  onClick={() => handleEscalate("access_lockout")}
                  disabled={disabled}
                  className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
                >
                  {action} →
                </button>
              );
            }
            return null;
          })}
      </div>
    );
  }

  const isFindStep = decision === "employer";

  const findStepView = isFindStep ? (
    <div className="w-full text-left">
      {error && (
        <div
          className={`mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 ${
            isSandbox ? "" : "mx-auto max-w-lg"
          }`}
        >
          {error}
        </div>
      )}
      <FindEmployerStep
        employer={employerInput}
        onEmployerChange={(value) => {
          setEmployerInput(value);
          if (error) setError(null);
        }}
        onSearch={handlePrimary}
        onKnowProvider={() => setShowProviderPicker(true)}
        onAskQuestion={() => setAssistantOpen(true)}
        searchLabel={screen.primary_action}
        loading={disabled}
        showKnowProvider={screen.secondary_actions.some((a) =>
          a.toLowerCase().includes("provider")
        )}
        showPerk={screen.body.includes("1%")}
        embedded={isSandbox}
      />
    </div>
  ) : null;

  const stepTransitionKey = `${screen.state}-${step_index}-${decision}`;

  const journeyCard = (
    <div
      className={
        isSandbox
          ? "text-left"
          : `pb-card p-8 sm:p-10 ${theme === "minimal" ? "shadow-none" : "lg:shadow-card-lg"}`
      }
    >
      <StepTransition stepKey={stepTransitionKey}>
      {showProgress && !isFindStep && <ProgressSteps current={screen.phase} />}

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <SourceStatusBadge status={sourceStatus} />
      </div>

      <LookupBanner data={data} />

      {(screen.provider || context.uncovered_provider) &&
        !["provider_identified", "provider_not_covered", "provider_unknown"].includes(
          screen.state
        ) &&
        !inChannel && (
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-bee-muted lg:text-base">
            {screen.provider || context.uncovered_provider}
            {screen.channel && ` · ${screen.channel}`}
            {!screen.provider && context.uncovered_provider && " · general guide"}
          </p>
        )}

      {inChannel && total_steps > 0 && (
        <ChannelStepHeader
          stepIndex={step_index}
          totalSteps={total_steps}
          provider={screen.provider || context.uncovered_provider || ""}
          channelLabel={channelLabel}
        />
      )}

      {!isFindStep && !inChannel && (
        <h1 className="mb-3 text-2xl font-bold leading-tight text-bee-charcoal lg:text-3xl lg:leading-snug">
          {screen.headline}
        </h1>
      )}

      {screen.body && !inChannel && decision !== "disambiguation" && !isFindStep && (
        <p className="mb-5 whitespace-pre-line text-base leading-relaxed text-bee-ink lg:text-lg">
          {screen.body}
        </p>
      )}

      {screen.state === "provider_not_covered" && decision === "access" && (
        <div className="mb-5 rounded-card border border-bee-yellow/50 bg-bee-yellow-soft/60 p-4 lg:p-5">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-bee-muted">
            General rollover guide
          </p>
          <p className="text-sm leading-relaxed text-bee-ink lg:text-base">
            {context.uncovered_provider
              ? `Your plan is with ${context.uncovered_provider}. We'll use our general online or phone steps — a BeeKeeper is available if you get stuck.`
              : "We'll use our general online or phone rollover steps for your provider."}
          </p>
        </div>
      )}

      <EdgeCaseAlerts
        items={inChannel && step_index > 0 ? [] : screen.edge_cases}
      />
      <ProvenanceBadge warning={screen.provenance_warning} />

      {inChannel && (
        <ChannelWalkthrough
          enrichment={enrichment}
          stepIndex={step_index}
          totalSteps={total_steps}
          surface={channelSurface}
        />
      )}

      {screen.state === "access_blocked" && screen.guidance?.length > 0 && (
        <ol className="mb-5 space-y-2">
          {screen.guidance.map((g, i) => (
            <li
              key={i}
              className={`flex gap-3 rounded-card px-4 py-3 text-sm lg:text-base ${
                g.reconstructed
                  ? "border-2 border-amber-400/80 bg-amber-50/80"
                  : "border border-bee-border bg-cream-dark/40"
              }`}
            >
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bee-charcoal text-xs font-bold text-white">
                {i + 1}
              </span>
              <span>
                {g.text}
                {g.reconstructed && (
                  <span className="mt-1 block text-xs font-semibold text-amber-800">
                    Double-check — phone menus can vary.
                  </span>
                )}
              </span>
            </li>
          ))}
        </ol>
      )}

      {(screen.phase === "track" || screen.state === "initiated") && (
        <TrackPanel enrichment={enrichment} />
      )}

      {error && (
        <div className="mb-4 rounded-card border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 lg:text-base">
          {error}
        </div>
      )}

      {decision !== "done" && !isFindStep && !readOnly && (
        <div className="mt-8 space-y-4">
          {renderDecision()}
          {!hideAssistant && (
            <button
              type="button"
              onClick={() => setAssistantOpen(true)}
              className="pb-interactive w-full py-4 text-center text-sm font-semibold text-bee-muted hover:text-[#1E242B] lg:text-base"
            >
              Ask a question about this step
            </button>
          )}
        </div>
      )}

      {screen.state === "complete" && (
        <div className="mt-4 rounded-card border border-bee-yellow/50 bg-bee-yellow-soft p-6 text-center lg:p-8">
          <p className="text-4xl lg:text-5xl">🎉</p>
          <p className="mt-2 text-lg font-bold text-bee-charcoal lg:text-xl">You&apos;re all set!</p>
          {screen.body.includes("1%") && (
            <p className="mt-2 text-sm text-bee-muted lg:text-base">
              You earned your 1% match — welcome to PensionBee.
            </p>
          )}
        </div>
      )}

      {screen.state === "escalated" && (
        <div className="mt-4 rounded-card border border-bee-yellow bg-bee-yellow-soft p-6 text-center lg:p-8">
          <p className="text-lg font-bold text-bee-charcoal">A BeeKeeper will take it from here</p>
          <p className="mt-2 text-sm text-bee-muted lg:text-base">{screen.body}</p>
        </div>
      )}
      </StepTransition>
    </div>
  );

  const themeClass =
    theme === "dark"
      ? "embed-theme-dark rounded-2xl bg-[#1E242B] p-4 text-white"
      : theme === "minimal"
        ? ""
        : "";

  return (
    <div className={themeClass}>
      {!hideAssistant && !readOnly && (
        <AssistantDrawer
          journeyId={context.journey_id}
          screen={screen}
          open={assistantOpen}
          onClose={() => setAssistantOpen(false)}
          onEscalate={() => {
            setAssistantOpen(false);
            act({ type: "escalate", reason: "assistant_handoff" });
          }}
        />
      )}

      {isAgent ? (
        <div className="grid gap-6 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-7">{isFindStep ? findStepView : journeyCard}</div>
          <div className="lg:col-span-5">
            <AgentPanel data={data} />
          </div>
        </div>
      ) : isFindStep ? (
        findStepView
      ) : (
        journeyCard
      )}
    </div>
  );
}
