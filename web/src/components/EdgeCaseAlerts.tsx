export function EdgeCaseAlerts({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="mb-5 space-y-2">
      <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">Good to know</p>
      {items.map((item, i) => (
        <div
          key={i}
          className="flex gap-3 rounded-block border border-bee-border bg-cream-dark/40 px-4 py-3 text-sm text-bee-ink lg:text-base"
        >
          <span className="mt-0.5 text-bee-muted" aria-hidden>
            ·
          </span>
          <p>{item}</p>
        </div>
      ))}
    </div>
  );
}
