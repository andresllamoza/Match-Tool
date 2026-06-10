import type { ReactNode } from "react";

export function StepDecisionFrame({
  title,
  helper,
  children,
}: {
  title: string;
  helper?: string | null;
  children: ReactNode;
}) {
  return (
    <div className="space-y-6 text-left">
      <div className="space-y-2">
        <p className="text-base font-semibold text-[#1E242B] lg:text-lg">{title}</p>
        {helper && (
          <p className="text-sm leading-relaxed text-[#6B6560] lg:text-base">{helper}</p>
        )}
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}
