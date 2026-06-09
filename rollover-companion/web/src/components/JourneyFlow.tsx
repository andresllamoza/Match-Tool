"use client";

import { useCallback, useEffect, useState } from "react";
import { journeyAction, startJourney } from "@/lib/api";
import type { JourneyResponse } from "@/lib/types";
import { AgentPanel } from "./AgentPanel";
import { AssistantDrawer } from "./AssistantDrawer";
import { ProgressSteps } from "./ProgressSteps";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { Button } from "./ui/Button";

interface JourneyFlowProps {
  mode?: "customer" | "agent" | "embed";
  theme?: "default" | "minimal";
  onPhaseChange?: (phase: import("@/lib/types").JourneyPhase) => void;
}

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

  const { screen, context, step_index, total_steps } = data;
  const showProgress = screen.state !== "complete" && screen.state !== "escalated";

  async function handlePrimary() {
    const s = screen.state;
    const primary = screen.primary_action.toLowerCase();

    if (s === "provider_unknown" && primary.includes("search")) {
      if (!employerInput.trim()) return;
      await act({ type: "lookup", employer: employerInput.trim() });
      return;
    }
    if (s === "provider_identified" && primary.includes("yes")) {
      await act({ type: "access", can_login: true });
      return;
    }
    if (s === "access_blocked" && primary.includes("in now")) {
      await act({ type: "access_recovered" });
      return;
    }
    if (s === "access_recovered" && primary.includes("online")) {
      await act({ type: "channel", channel: "online" });
      return;
    }
    if (
      ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(s) &&
      primary.includes("done")
    ) {
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
    if (s === "escalated") {
      return;
    }
  }

  async function handleSecondary(label: string) {
    const lower = label.toLowerCase();
    const s = screen.state;

    if (lower.includes("provider") && s === "provider_unknown") {
      setShowProviderPicker(true);
      return;
    }
    if (lower.includes("no") && s === "provider_identified") {
      await act({ type: "access", can_login: false });
      return;
    }
    if (lower.includes("locked out") || lower.includes("beekeeper")) {
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
    if (lower.includes("nothing arrived") || lower.includes("help")) {
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
        theme === "minimal" ? "shadow-none border border-bee-border" : "lg:shadow-card-lg"
      }`}
    >
      {showProgress && <ProgressSteps current={screen.phase} />}

      {screen.provider && (
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-bee-muted lg:text-base">
          {screen.provider}
          {screen.channel && ` · ${screen.channel}`}
        </p>
      )}

      <h1 className="mb-3 text-2xl font-bold leading-tight text-bee-blue lg:text-3xl lg:leading-snug">
        {screen.headline}
      </h1>

      {screen.body && (
        <p className="mb-5 text-base leading-relaxed text-bee-ink lg:text-lg lg:leading-relaxed">
          {screen.body}
        </p>
      )}

      <ProvenanceBadge warning={screen.provenance_warning} />

      {total_steps > 0 && (
        <div className="mb-5">
          <div className="mb-2 flex justify-between text-xs font-medium text-bee-muted lg:text-sm">
            <span>Progress</span>
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

      {screen.guidance?.length > 0 && (
        <ul className="mb-5 space-y-2">
          {screen.guidance.map((g, i) => (
            <li
              key={i}
              className={`rounded-card px-4 py-3 text-sm lg:text-base ${
                g.reconstructed
                  ? "border border-dashed border-amber-300 bg-amber-50/50"
                  : "bg-cream"
              }`}
            >
              {g.text}
              {g.reconstructed && (
                <span className="ml-2 text-xs font-semibold text-amber-700">
                  · double-check
                </span>
              )}
            </li>
          ))}
        </ul>
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

      {screen.sla_note && screen.phase === "track" && (
        <p className="mb-4 text-sm text-bee-muted lg:text-base">
          <span className="font-semibold">Timeline:</span> {screen.sla_note}
        </p>
      )}

      {error && (
        <div className="mb-4 rounded-card bg-red-50 px-4 py-3 text-sm text-red-800 lg:text-base">
          {error} A BeeKeeper can help.
        </div>
      )}

      {screen.state !== "complete" && (
        <div className="space-y-3">
          <Button onClick={handlePrimary} disabled={loading}>
            {screen.primary_action}
          </Button>
          {screen.secondary_actions.map((action) => (
            <Button
              key={action}
              variant="secondary"
              onClick={() => handleSecondary(action)}
              disabled={loading}
            >
              {action}
            </Button>
          ))}
          {screen.state !== "escalated" && (
            <button
              type="button"
              onClick={() => setAssistantOpen(true)}
              className="w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-blue lg:text-base"
            >
              Ask a question
            </button>
          )}
        </div>
      )}

      {screen.state === "complete" && (
        <div className="mt-4 rounded-card bg-bee-blue-light p-6 text-center lg:p-8">
          <p className="text-4xl lg:text-5xl">🎉</p>
          <p className="mt-2 text-lg font-bold text-bee-blue lg:text-xl">You&apos;re all set!</p>
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
