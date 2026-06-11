export function NextStepBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-pill bg-bee-pink px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.08em] text-bee-charcoal">
      {children}
    </span>
  );
}
