import type { PathHistoryEntry } from "@/lib/pathHistory";
import type { JourneyResponse } from "@/lib/types";

export function AgentPathHistoryPanel({
  data,
  pathHistory,
  stalledStep,
}: {
  data: JourneyResponse;
  pathHistory: PathHistoryEntry[];
  stalledStep?: number | null;
}) {
  const { context, screen, enrichment } = data;
  const payee =
    enrichment.channel_context?.check_payable ||
    (enrichment.customer_display_name
      ? `PensionBee FBO ${enrichment.customer_display_name}`
      : null);

  return (
    <div className="overflow-hidden rounded-xl border border-[#EAE5DC] bg-white">
      <div className="border-b border-[#EAE5DC] bg-[#FAF8F5] px-5 py-4">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          Customer path log
        </p>
        <p className="mt-1 text-sm text-[#555555]">
          Live trail from Surface 1 — employer, provider, and stall point.
        </p>
      </div>

      <dl className="grid gap-4 px-5 py-4 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Employer searched
          </dt>
          <dd className="mt-1 font-semibold text-[#1E242B]">
            {context.employer_query || "—"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Provider
          </dt>
          <dd className="mt-1 font-semibold text-[#1E242B]">
            {screen.provider || context.uncovered_provider || "—"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            Stalled on
          </dt>
          <dd className="mt-1 font-semibold text-[#1E242B]">
            {stalledStep != null
              ? `Step ${stalledStep + 1} · ${screen.headline}`
              : screen.state === "escalated"
                ? screen.headline
                : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-bold uppercase tracking-wide text-[#6B6560]">
            FBO payee line
          </dt>
          <dd className="mt-1 font-semibold text-[#1E242B]">{payee || "—"}</dd>
        </div>
      </dl>

      <div className="max-h-48 overflow-y-auto border-t border-[#EAE5DC] px-5 py-3">
        {pathHistory.length === 0 ? (
          <p className="text-sm text-[#6B6560]">No transitions yet — interact in Surface 1.</p>
        ) : (
          <ol className="space-y-2">
            {pathHistory.map((entry, i) => (
              <li
                key={`${entry.at}-${i}`}
                className="rounded-lg border border-[#EAE5DC] bg-[#FAF8F5] px-3 py-2 text-xs leading-relaxed text-[#1E242B]"
              >
                <span className="font-semibold text-[#111111]">{entry.action}</span>
                {" · "}
                {entry.state}
                {entry.stepIndex > 0 || entry.state.includes("progress")
                  ? ` · step ${entry.stepIndex + 1}`
                  : ""}
                {entry.provider ? ` · ${entry.provider}` : ""}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  );
}
