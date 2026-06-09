"use client";

import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "beekeeper";

const styles: Record<Variant, string> = {
  primary:
    "bg-bee-charcoal text-white hover:bg-bee-ink shadow-sm active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-bee-yellow focus-visible:ring-offset-2 focus-visible:ring-offset-canvas",
  secondary:
    "bg-white text-bee-charcoal border-2 border-bee-border hover:border-bee-charcoal/30 hover:bg-cream-dark/50 active:scale-[0.98]",
  ghost: "bg-transparent text-bee-ink hover:bg-bee-yellow-soft/60 active:scale-[0.98]",
  danger:
    "bg-white text-red-800 border-2 border-red-200 hover:bg-red-50 active:scale-[0.98]",
  beekeeper:
    "bg-bee-yellow-soft text-bee-charcoal border-2 border-bee-yellow hover:bg-bee-yellow/40 active:scale-[0.98]",
};

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`w-full min-h-[52px] rounded-card px-5 py-3.5 text-base font-semibold transition-transform duration-150 disabled:cursor-not-allowed disabled:opacity-50 lg:min-h-[56px] lg:py-4 lg:text-lg ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
