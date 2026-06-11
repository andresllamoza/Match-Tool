"use client";

import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "beekeeper";

const styles: Record<Variant, string> = {
  primary:
    "bg-bee-yellow text-bee-charcoal hover:bg-bee-yellow-hover shadow-sm pb-cta font-extrabold pb-focus-ring",
  secondary:
    "bg-white text-bee-ink border-2 border-bee-border hover:border-bee-charcoal/30 hover:bg-cream-dark/50 pb-focus-ring",
  ghost:
    "bg-transparent text-bee-ink hover:bg-bee-yellow-soft/60 pb-focus-ring",
  danger:
    "bg-white text-bee-ink border-2 border-bee-border hover:bg-cream-dark pb-focus-ring",
  beekeeper:
    "bg-bee-charcoal text-white hover:bg-bee-ink shadow-sm pb-focus-ring",
};

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`w-full min-h-[56px] rounded-cta px-6 py-4 text-base disabled:cursor-not-allowed disabled:opacity-50 lg:min-h-[56px] lg:px-8 lg:py-4 lg:text-lg ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
