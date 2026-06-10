"use client";

import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "beekeeper";

const styles: Record<Variant, string> = {
  primary:
    "bg-[#111111] text-white hover:bg-[#1E242B] shadow-sm transition-all duration-200 ease-out active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-bee-yellow focus-visible:ring-offset-2 focus-visible:ring-offset-canvas",
  secondary:
    "bg-white text-[#1E242B] border-2 border-bee-border hover:border-bee-charcoal/30 hover:bg-cream-dark/50 transition-all duration-200 ease-out active:scale-[0.98]",
  ghost:
    "bg-transparent text-[#1E242B] hover:bg-bee-yellow-soft/60 transition-all duration-200 ease-out active:scale-[0.98]",
  danger:
    "bg-white text-red-800 border-2 border-red-200 hover:bg-red-50 transition-all duration-200 ease-out active:scale-[0.98]",
  beekeeper:
    "bg-bee-yellow-soft text-bee-charcoal border-2 border-bee-yellow hover:bg-bee-yellow/40 transition-all duration-200 ease-out active:scale-[0.98]",
};

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`w-full min-h-[52px] rounded-card px-6 py-4 text-base font-semibold disabled:cursor-not-allowed disabled:opacity-50 lg:min-h-[56px] lg:px-8 lg:py-4 lg:text-lg ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
