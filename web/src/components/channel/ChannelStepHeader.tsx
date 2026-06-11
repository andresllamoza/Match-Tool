export function ChannelStepHeader({
  stepIndex,
  totalSteps,
  provider,
  channelLabel,
  instruction,
}: {
  stepIndex: number;
  totalSteps: number;
  provider: string;
  channelLabel: string;
  instruction?: string;
}) {
  const progress =
    totalSteps > 0 ? Math.round(((stepIndex + 1) / totalSteps) * 100) : 0;

  const meta = [
    `Step ${stepIndex + 1} of ${totalSteps}`,
    provider || null,
    channelLabel || null,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <header className="mb-8">
      <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
        {meta}
      </p>
      {instruction && (
        <h1 className="text-2xl font-extrabold leading-[1.15] tracking-[-0.03em] text-bee-charcoal sm:text-3xl">
          {instruction}
        </h1>
      )}
      {totalSteps > 0 && (
        <div
          className={`h-[3px] overflow-hidden rounded-full bg-cream-dark ${instruction ? "mt-5" : "mt-3"}`}
          role="progressbar"
          aria-valuenow={stepIndex + 1}
          aria-valuemin={1}
          aria-valuemax={totalSteps}
        >
          <div
            className="h-full rounded-full bg-bee-yellow transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </header>
  );
}
