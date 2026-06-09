import type { JourneyResponse } from "@/lib/types";

interface AgentPanelProps {
  data: JourneyResponse;
}

export function AgentPanel({ data }: AgentPanelProps) {
  const { screen, context, provider_intel, step_index, total_steps } = data;
  const repQuestions = (provider_intel.rep_questions as { question: string; answer: string }[]) || [];

  return (
    <aside className="space-y-4 lg:sticky lg:top-8 lg:max-h-[calc(100dvh-4rem)] lg:overflow-y-auto">
      <div className="rounded-card border border-bee-blue/15 bg-white p-5 shadow-card lg:p-6">
        <h2 className="mb-3 text-sm font-bold uppercase tracking-wide text-bee-blue">
          BeeKeeper intel
        </h2>
        <dl className="space-y-2 text-sm lg:text-base">
          <div className="flex justify-between gap-4">
            <dt className="text-bee-muted">State</dt>
            <dd className="font-mono text-xs font-semibold text-bee-ink lg:text-sm">
              {screen.state}
            </dd>
          </div>
          {context.provider && (
            <div className="flex justify-between gap-4">
              <dt className="text-bee-muted">Provider</dt>
              <dd className="font-semibold">{context.provider}</dd>
            </div>
          )}
          {context.channel && (
            <div className="flex justify-between gap-4">
              <dt className="text-bee-muted">Channel</dt>
              <dd className="font-semibold capitalize">{context.channel}</dd>
            </div>
          )}
          {total_steps > 0 && (
            <div className="flex justify-between gap-4">
              <dt className="text-bee-muted">Step</dt>
              <dd className="font-semibold">
                {step_index + 1} / {total_steps}
              </dd>
            </div>
          )}
        </dl>
      </div>

      {screen.next_beekeeper_script && (
        <div className="rounded-card border-2 border-bee-yellow bg-bee-yellow/10 p-5 lg:p-6">
          <h3 className="mb-2 font-bold text-bee-ink">Say this next</h3>
          <p className="text-sm leading-relaxed lg:text-base">{screen.next_beekeeper_script}</p>
        </div>
      )}

      {screen.agent_notes.length > 0 && (
        <div className="rounded-card bg-white p-5 shadow-card lg:p-6">
          <h3 className="mb-2 font-bold text-bee-blue">Agent notes</h3>
          <ul className="space-y-2 text-sm lg:text-base">
            {screen.agent_notes.map((note, i) => (
              <li key={i} className="flex gap-2 text-bee-ink">
                <span className="text-bee-blue">•</span>
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}

      {screen.edge_cases.length > 0 && (
        <div className="rounded-card border border-amber-200 bg-amber-50 p-5 lg:p-6">
          <h3 className="mb-2 font-bold text-amber-900">Edge cases</h3>
          <ul className="space-y-1 text-sm text-amber-900 lg:text-base">
            {screen.edge_cases.map((ec, i) => (
              <li key={i}>⚡ {ec}</li>
            ))}
          </ul>
        </div>
      )}

      {repQuestions.length > 0 && (
        <div className="rounded-card bg-white p-5 shadow-card lg:p-6">
          <h3 className="mb-2 font-bold text-bee-blue">Rep will ask</h3>
          <dl className="space-y-3 text-sm lg:text-base">
            {repQuestions.map((q, i) => (
              <div key={i}>
                <dt className="font-semibold text-bee-ink">{q.question}</dt>
                <dd className="mt-0.5 text-bee-muted">{q.answer}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {typeof provider_intel.mechanism === "string" && (
        <div className="rounded-card bg-bee-blue-light/40 p-5 text-sm lg:p-6 lg:text-base">
          <p>
            <span className="font-semibold">Mechanism:</span>{" "}
            {provider_intel.mechanism.replace(/_/g, " ")}
          </p>
          <p className="mt-1">
            <span className="font-semibold">Check:</span>{" "}
            {String(provider_intel.check_destination ?? "")}
          </p>
        </div>
      )}
    </aside>
  );
}
