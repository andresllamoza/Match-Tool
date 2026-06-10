export function ProvenanceBadge({ warning }: { warning: string | null }) {
  if (!warning) return null;
  return (
    <div className="mb-4 flex items-start gap-2 rounded-card border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 lg:text-base">
      <span aria-hidden>⚠️</span>
      <p>{warning}</p>
    </div>
  );
}
