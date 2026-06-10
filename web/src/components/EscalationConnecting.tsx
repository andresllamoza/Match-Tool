export function EscalationConnecting() {
  return (
    <div
      className="absolute inset-0 z-20 flex items-center justify-center rounded-2xl bg-white/90 backdrop-blur-[2px]"
      role="status"
      aria-live="polite"
      aria-label="Connecting to BeeKeeper"
    >
      <div className="px-8 text-center">
        <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-[#FFC72C]/30 border-t-[#FFC72C]" />
        <p className="text-base font-semibold text-[#1E242B] sm:text-lg">
          Connecting you with a rollover specialist…
        </p>
        <p className="mt-2 text-sm text-[#6B6560]">
          A BeeKeeper is reviewing your exact step and provider path.
        </p>
      </div>
    </div>
  );
}
