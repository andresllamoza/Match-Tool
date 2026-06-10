export function ChannelStepHeader({
  stepIndex,
  totalSteps,
  provider,
  channelLabel,
}: {
  stepIndex: number;
  totalSteps: number;
  provider: string;
  channelLabel: string;
}) {
  const progress =
    totalSteps > 0 ? Math.round(((stepIndex + 1) / totalSteps) * 100) : 0;

  return (
    <header className="mb-5">
      <p className="text-xl font-medium tracking-tight text-gray-500">
        Step {stepIndex + 1} of {totalSteps}
        {provider ? ` · ${provider}` : ""}
        {channelLabel ? ` · ${channelLabel}` : ""}
      </p>
      {totalSteps > 0 && (
        <div
          className="mt-3 h-2 overflow-hidden rounded-full bg-[#F3EDE4]"
          role="progressbar"
          aria-valuenow={stepIndex + 1}
          aria-valuemin={1}
          aria-valuemax={totalSteps}
        >
          <div
            className="h-full rounded-full bg-[#FFC72C] transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </header>
  );
}
