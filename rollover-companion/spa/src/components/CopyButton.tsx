import { useState } from "react";

export function CopyButton({ value, label = "Copy" }: { value: string; label?: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      type="button"
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setDone(true);
        setTimeout(() => setDone(false), 2000);
      }}
      className={`shrink-0 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors ${
        done
          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
          : "border-border text-muted hover:border-ink/20 hover:text-ink"
      }`}
    >
      {done ? "✓ Copied" : label}
    </button>
  );
}
