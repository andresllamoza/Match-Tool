"use client";

const NAV = [
  { id: "summary", label: "Summary" },
  { id: "iras", label: "My IRAs" },
  { id: "actions", label: "Actions", active: true },
  { id: "discover", label: "Discover" },
] as const;

export function PensionBeeSidebar() {
  return (
    <aside
      className="hidden w-56 shrink-0 flex-col rounded-card border border-bee-border bg-cream-dark/40 p-4 lg:flex"
      aria-label="PensionBee navigation"
    >
      <p className="mb-6 px-2 text-lg font-extrabold tracking-tight text-bee-charcoal">PensionBee</p>
      <nav className="flex flex-col gap-1">
        {NAV.map((item) => (
          <span
            key={item.id}
            className={`rounded-pill px-3 py-2.5 text-sm font-semibold ${
              "active" in item && item.active
                ? "bg-white text-bee-charcoal shadow-sm"
                : "text-bee-muted"
            }`}
            aria-current={"active" in item && item.active ? "page" : undefined}
          >
            {item.label}
          </span>
        ))}
      </nav>
    </aside>
  );
}
