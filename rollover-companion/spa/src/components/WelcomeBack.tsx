export function WelcomeBack({ onDismiss }: { onDismiss: () => void }) {
  return (
    <div className="mb-6 animate-[slideIn_0.4s_ease-out] rounded-2xl border border-border bg-white p-5 shadow-card">
      <p className="text-xs font-bold uppercase tracking-wider text-[#9A6200]">Welcome back</p>
      <p className="mt-2 text-[17px] leading-relaxed text-ink">
        We saved your spot — pick up where you left off.
      </p>
      <button type="button" onClick={onDismiss} className="mt-3 text-sm font-semibold text-muted hover:text-ink">
        Got it
      </button>
    </div>
  );
}
