export function ProvenanceBadge({ warning }: { warning: string | null }) {
  if (!warning) return null;
  return (
    <div className="mb-4 flex items-start gap-2 rounded-block border border-bee-border bg-cream-dark/50 px-4 py-3 text-sm text-bee-ink lg:text-base">
      <span className="font-bold text-bee-muted" aria-hidden>
        i
      </span>
      <p>{warning}</p>
    </div>
  );
}
