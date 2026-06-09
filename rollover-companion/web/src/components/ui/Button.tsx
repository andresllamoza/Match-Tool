"use client";

import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const styles: Record<Variant, string> = {
  primary:
    "bg-bee-blue text-white hover:bg-bee-blue-hover shadow-sm active:scale-[0.98]",
  secondary:
    "bg-white text-bee-blue border-2 border-bee-blue/20 hover:border-bee-blue/40 hover:bg-bee-blue-light/50",
  ghost: "bg-transparent text-bee-blue hover:bg-bee-blue-light/60",
  danger: "bg-red-50 text-red-700 border border-red-200 hover:bg-red-100",
};

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`w-full rounded-card px-5 py-3.5 text-base font-semibold transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed lg:py-4 lg:text-lg ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
