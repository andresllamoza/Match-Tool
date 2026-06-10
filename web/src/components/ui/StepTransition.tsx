"use client";

import { ReactNode } from "react";

export function StepTransition({
  stepKey,
  children,
  className = "",
}: {
  stepKey: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div key={stepKey} className={`pb-step-enter ${className}`}>
      {children}
    </div>
  );
}
