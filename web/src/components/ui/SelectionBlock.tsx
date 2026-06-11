"use client";

interface SelectionBlockProps {
  label: string;
  description?: string;
  selected?: boolean;
  recommended?: boolean;
  onClick: () => void;
  disabled?: boolean;
}

export function SelectionBlock({
  label,
  description,
  selected,
  recommended,
  onClick,
  disabled,
}: SelectionBlockProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`pb-select-card flex min-h-[72px] w-full flex-col justify-center rounded-block border-2 px-6 py-5 text-left disabled:opacity-50 sm:px-8 sm:py-6 ${
        recommended
          ? "border-bee-yellow bg-bee-yellow-tint shadow-sm"
          : selected
            ? "border-bee-charcoal bg-bee-yellow-tint shadow-sm"
            : "border-bee-border bg-white hover:border-bee-charcoal hover:bg-cream-dark/30"
      }`}
    >
      <span className="text-base font-semibold leading-snug text-[#1E242B] lg:text-lg">
        {label}
      </span>
      {description && (
        <span className="mt-1 text-sm leading-relaxed text-bee-muted">{description}</span>
      )}
    </button>
  );
}
