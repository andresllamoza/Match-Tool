"use client";

interface SelectionBlockProps {
  label: string;
  description?: string;
  selected?: boolean;
  onClick: () => void;
  disabled?: boolean;
}

export function SelectionBlock({
  label,
  description,
  selected,
  onClick,
  disabled,
}: SelectionBlockProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`flex min-h-[64px] w-full flex-col justify-center rounded-card border-2 px-5 py-4 text-left transition-all duration-150 active:scale-[0.98] disabled:opacity-50 ${
        selected
          ? "border-bee-charcoal bg-bee-yellow-soft/50 shadow-sm"
          : "border-bee-border bg-white hover:border-bee-charcoal/25 hover:bg-cream-dark/30"
      }`}
    >
      <span className="text-base font-semibold leading-snug text-bee-charcoal lg:text-lg">
        {label}
      </span>
      {description && (
        <span className="mt-1 text-sm leading-relaxed text-bee-muted">{description}</span>
      )}
    </button>
  );
}
