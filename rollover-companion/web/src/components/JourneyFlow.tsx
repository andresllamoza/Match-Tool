"use client";

import { useCallback, useEffect, useState } from "react";
import { journeyAction, startJourney } from "@/lib/api";
import type { JourneyResponse } from "@/lib/types";
import { AgentPanel } from "./AgentPanel";
import { AssistantDrawer } from "./AssistantDrawer";
import { ChannelWalkthrough } from "./ChannelWalkthrough";
import { EdgeCaseAlerts } from "./EdgeCaseAlerts";
import { LookupBanner } from "./LookupBanner";
import { ProgressSteps } from "./ProgressSteps";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { TrackPanel } from "./TrackPanel";
import { Button } from "./ui/Button";

interface JourneyFlowProps {
  mode?: "customer" | "agent" | "embed";
  theme?: "default" | "minimal";
  onPhaseChange?: (phase: import("@/lib/types").JourneyPhase) => void;
}

const TAX_MAP: Record<string, string> = {
  "pre-tax (traditional ira)": "pre_tax",
  "roth (roth ira)": "roth",
  "both pre-tax and roth": "both",
  "pre-tax into a roth ira": "pre_tax_to_roth",
};

export function JourneyFlow({ mode = "customer", theme = "default", onPhaseChange }: JourneyFlowProps) {
  const isAgent = mode === "agent";
  const [data, setData] = useState<JourneyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [employerInput, setEmployerInput] = useState("");
  const [showProviderPicker, setShowProviderPicker] = useState(false);
  const [providers, setProviders] = useState<string[]>([]);
  const [assistantOpen, setAssistantOpen] = useState(false);

  const act = useCallback(
    async (body: Record<string, unknown>) => {
      if (!data) return;
      setLoading(true);
      setError(null);
      try {
        const res = await journeyAction(data.context.journey_id, body, isAgent);
        setData(res);
        onPhaseChange?.(res.screen.phase);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong. A BeeKeeper can help.");
      } finally {
        setLoading(false);
      }
    },
    [data, isAgent, onPhaseChange]
  );

  useEffect(() => {
    (async () => {
      try {
        const res = await startJourney(isAgent);
        setData(res);
        onPhaseChange?.(res.screen.phase);
        const prov = await fetch("/api/providers").then((r) => r.json());
        setProviders(prov.providers || []);
      } catch {
        setError("Could not connect to the rollover engine. A BeeKeeper can help.");
      } finally {
        setLoading(false);
      }
    })();
  }, [isAgent, onPhaseChange]);

  if (loading && !data) {
    return (
      <div className="flex min-h-[50dvh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-blue/20 border-t-bee-blue" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-card bg-red-50 p-6 text-center text-red-800">
        {error || "Unable to start journey."}
      </div>
    );
  }

  const { screen, context, step_index, total_steps, enrichment } = data;
  const showProgress = screen.state !== "complete" && screen.state !== "escalated";
  const inChannel = ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(
    screen.state
  );
  const taxPending = enrichment.requires_tax_selection;

  async function handlePrimary() {
    const s = screen.state;
    const primary = screen.primary_action.toLowerCase();

    if (s === "provider_unknown" && primary.includes("search")) {
      if (!employerInput.trim()) return;
      await act({ type: "lookup", employer: employerInput.trim() });
      return;
    }
    if (taxPending && primary.includes("pre-tax")) {
      await act({ type: "tax_type", tax_type: "pre_tax" });
      return;
    }
    if ((s === "provider_identified" || s === "provider_not_covered") && primary.includes("yes")) {
      await act({ type: "access", can_login: true });
      return;
    }
    if (s === "access_blocked" && primary.includes("in now")) {
      await act({ type: "access_recovered" });
      return;
    }
    if (s === "access_recovered" && !taxPending && primary.includes("online")) {
      await act({ type: "channel", channel: "online" });
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
  }

  async function handleSecondary(label: string) {
    const lower = label.toLowerCase();
    const s = screen.state;

    if (taxPending) {
      const taxType = TAX_MAP[lower] || Object.entries(TAX_MAP).find(([k]) => lower.includes(k))?.[1];
      if (taxType) {
        await act({ type: "tax_type", tax_type: taxType });
        return;
      }
    }
    if (lower.includes("provider") && s === "provider_unknown") {
      setShowProviderPicker(true);
      return;
    }
    if (lower.includes("no") && (s === "provider_identified" || s === "provider_not_covered")) {
      await act({ type: "access", can_login: false });
      return;
    }
    if (lower.includes("beekeeper") && s === "provider_not_covered") {
      await act({ type: "handoff", reason: "provider_not_covered" });
      return;
    }
    if (lower.includes("locked out") || (lower.includes("beekeeper") && s === "access_blocked")) {
      await act({ type: "escalate", reason: "access_lockout" });
      return;
    }
    if (lower === "phone") {
      await act({ type: "channel", channel: "phone" });
      return;
    }
    if (lower.includes("form")) {
      await act({ type: "channel", channel: "forms" });
      return;
    }
    if (lower.includes("stuck")) {
      await act({ type: "step", outcome: "stuck" });
      return;
    }
    if (lower.includes("try again")) {
      await act({ type: "resume" });
      return;
    }
    if (lower.includes("nothing arrived") || lower.includes("get help")) {
      await act({ type: "escalate", reason: "tracking_delay" });
      return;
    }
  }

  async function handleDisambiguation(option: string) {
    await act({ type: "disambiguate", answer: option });
  }

  async function handleProviderPick(provider: string) {
    setShowProviderPicker(false);
    await act({ type: "provider_direct", provider });
  }

  const journeyCard = (
    <div
      className={`rounded-card bg-white p-6 shadow-card lg:p-10 ${
        theme === "minimal" ? "border border-bee-border shadow-none" : "lg:shadow-card-lg"
      }`}
    >
      {showProgress && <ProgressSteps current={screen.phase} />}

      <LookupBanner data={data} />

      {(screen.provider || context.uncovered_provider) &&
        !["provider_identified", "provider_not_covered"].includes(screen.state) && (
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-bee-muted lg:text-base">
          {screen.provider || context.uncovered_provider}
          {screen.channel && ` · ${screen.channel}`}
          {!screen.provider && context.uncovered_provider && " · general guide"}
        </p>
      )}

      <h1 className="mb-3 text-2xl font-bold leading-tight text-bee-blue lg:text-3xl lg:leading-snug">
        {screen.headline}
      </h1>

      {screen.body && !inChannel && (
        <p className="mb-5 whitespace-pre-line text-base leading-relaxed text-bee-ink lg:text-lg">
          {screen.body}
        </p>
      )}

      {screen.state === "provider_not_covered" && (
        <div className="mb-5 rounded-card border border-bee-blue/20 bg-bee-blue-light/40 p-4 lg:p-5">
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

      {screen.state === "provider_unknown" && screen.body.includes("1%") && (
        <div className="mb-5 rounded-card bg-bee-blue-light/70 p-4 lg:p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-bee-muted">PensionBee perk</p>
          <p className="mt-1 text-sm font-semibold text-bee-blue lg:text-base">
            Roll your old 401(k) to PensionBee and get a 1% match on eligible transfers.
          </p>
        </div>
      )}

      <EdgeCaseAlerts items={screen.edge_cases} />

      <ProvenanceBadge warning={screen.provenance_warning} />

      {inChannel && <ChannelWalkthrough enrichment={enrichment} />}

      {screen.state === "access_blocked" && screen.guidance?.length > 0 && (
        <ol className="mb-5 space-y-2">
          {screen.guidance.map((g, i) => (
            <li
              key={i}
              className={`flex gap-3 rounded-card px-4 py-3 text-sm lg:text-base ${
                g.reconstructed
                  ? "border border-dashed border-amber-300 bg-amber-50/50"
                  : "bg-cream"
              }`}
            >
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bee-blue text-xs font-bold text-white">
                {i + 1}
              </span>
              <span>
                {g.text}
                {g.reconstructed && (
                  <span className="ml-1 text-xs font-semibold text-amber-700">· double-check</span>
                )}
              </span>
            </li>
          ))}
        </ol>
      )}

      {(screen.phase === "track" || screen.state === "initiated") && (
        <TrackPanel enrichment={enrichment} />
      )}

      {total_steps > 0 && inChannel && (
        <div className="mb-5">
          <div className="mb-2 flex justify-between text-xs font-medium text-bee-muted lg:text-sm">
            <span>Step progress</span>
            <span>
              {step_index + 1} of {total_steps}
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-pill bg-cream-dark">
            <div
              className="h-full rounded-pill bg-bee-blue transition-all duration-300"
              style={{ width: `${((step_index + 1) / total_steps) * 100}%` }}
            />
          </div>
        </div>
      )}

      {screen.disambiguation_question && (
        <div className="mb-5 rounded-card bg-bee-blue-light/50 p-4 lg:p-5">
          <p className="mb-3 font-semibold text-bee-blue lg:text-lg">
            {screen.disambiguation_question}
          </p>
          <div className="space-y-2">
            {screen.disambiguation_options.map((opt) => (
              <Button key={opt} variant="secondary" onClick={() => handleDisambiguation(opt)}>
                {opt}
              </Button>
            ))}
          </div>
        </div>
      )}

      {showProviderPicker && (
        <div className="mb-5 space-y-2">
          <p className="font-semibold text-bee-blue">Select your 401(k) provider</p>
          {providers.map((p) => (
            <Button key={p} variant="secondary" onClick={() => handleProviderPick(p)}>
              {p}
            </Button>
          ))}
        </div>
      )}

      {(screen.state === "provider_unknown" ||
        (screen.disambiguation_question?.toLowerCase().includes("employer") &&
          screen.disambiguation_options.length === 0)) && (
        <div className="mb-5">
          <input
            value={employerInput}
            onChange={(e) => setEmployerInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handlePrimary()}
            placeholder="Former employer or provider name"
            className="mb-3 w-full rounded-card border border-bee-border bg-cream px-4 py-3.5 text-base outline-none focus:border-bee-blue focus:ring-2 focus:ring-bee-blue/20 lg:py-4 lg:text-lg"
          />
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-card bg-red-50 px-4 py-3 text-sm text-red-800 lg:text-base">
          {error} A BeeKeeper can help.
        </div>
      )}

      {screen.state !== "complete" && screen.state !== "escalated" && (
        <div className="space-y-3">
          <Button onClick={handlePrimary} disabled={loading}>
            {screen.primary_action}
          </Button>
          {screen.secondary_actions.map((action) => (
            <Button
              key={action}
              variant={action.toLowerCase().includes("stuck") ? "danger" : "secondary"}
              onClick={() => handleSecondary(action)}
              disabled={loading}
            >
              {action}
            </Button>
          ))}
          <button
            type="button"
            onClick={() => setAssistantOpen(true)}
            className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-blue lg:text-base"
          >
            Ask a question
          </button>
        </div>
      )}

      {screen.state === "complete" && (
        <div className="mt-4 rounded-card bg-bee-blue-light p-6 text-center lg:p-8">
          <p className="text-4xl lg:text-5xl">🎉</p>
          <p className="mt-2 text-lg font-bold text-bee-blue lg:text-xl">You&apos;re all set!</p>
          {screen.body.includes("1%") && (
            <p className="mt-2 text-sm text-bee-muted lg:text-base">
              You earned your 1% match — welcome to PensionBee.
            </p>
          )}
        </div>
      )}

      {screen.state === "escalated" && (
        <div className="mt-4 rounded-card bg-bee-yellow/20 p-6 text-center lg:p-8">
          <p className="text-lg font-bold text-bee-ink">A BeeKeeper will take it from here</p>
          <p className="mt-2 text-sm text-bee-muted lg:text-base">{screen.body}</p>
        </div>
      )}
    </div>
  );

  return (
    <>
      <AssistantDrawer
        journeyId={context.journey_id}
        open={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        onEscalate={() => {
          setAssistantOpen(false);
          act({ type: "escalate", reason: "assistant_handoff" });
        }}
      />

      {isAgent ? (
        <div className="grid gap-6 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-7">{journeyCard}</div>
          <div className="lg:col-span-5">
            <AgentPanel data={data} />
          </div>
        </div>
      ) : (
        journeyCard
      )}
    </>
  );
}
