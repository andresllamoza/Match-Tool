export function BeeKeeperCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="mt-6 rounded-2xl border border-border bg-[#FFF9E6] p-5">
      <p className="text-xs font-bold uppercase tracking-wider text-[#9A6200]">🐝 Your BeeKeeper</p>
      <p className="mt-2 text-[17px] leading-relaxed text-ink">{children}</p>
    </div>
  );
}
