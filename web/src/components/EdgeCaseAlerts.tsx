export function EdgeCaseAlerts({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="mb-5 space-y-2">
      <p className="text-xs font-bold uppercase tracking-wide text-amber-800">Heads up</p>
      {items.map((item, i) => (
        <div
          key={i}
          className="flex gap-3 rounded-card border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 lg:text-base"
        >
          <span className="text-lg leading-none" aria-hidden>
            ⚡
          </span>
          <p>{item}</p>
        </div>
      ))}
    </div>
  );
}
