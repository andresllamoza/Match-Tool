"use client";

interface InputFieldProps {
  label: string;
  helper: string;
  value: string;
  onChange: (value: string) => void;
  onSubmit?: () => void;
  placeholder?: string;
  disabled?: boolean;
}

export function InputField({
  label,
  helper,
  value,
  onChange,
  onSubmit,
  placeholder,
  disabled,
}: InputFieldProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-bee-charcoal lg:text-base">{label}</label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSubmit?.()}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full rounded-card border-2 border-bee-border bg-white px-4 py-4 text-base text-bee-charcoal outline-none transition-colors placeholder:text-bee-muted/70 focus:border-bee-yellow focus:ring-2 focus:ring-bee-yellow/30 lg:py-4 lg:text-lg"
      />
      <p className="text-sm leading-relaxed text-bee-muted">{helper}</p>
    </div>
  );
}
