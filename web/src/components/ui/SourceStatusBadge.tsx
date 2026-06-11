export function SourceStatusBadge({
  status,
}: {
  status: "verified" | "reconstructed" | null | undefined;
}) {
  if (!status) return null;

  if (status === "verified") {
    return (
      <span className="inline-flex items-center gap-1 rounded-lg border border-bee-border bg-white px-3 py-1.5 text-xs font-semibold text-bee-green shadow-sm lg:text-sm">
        <span aria-hidden>✓</span> Verified path
      </span>
    );
  }

  return (
    <div className="rounded-block border border-bee-border bg-cream-dark/50 px-5 py-4 text-sm leading-relaxed text-bee-ink shadow-sm lg:text-base">
      <p className="flex items-center gap-2 font-semibold text-bee-charcoal">
        <span
          className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-bee-border text-xs text-bee-muted"
          aria-hidden
        >
          i
        </span>
        Human verification recommended
      </p>
      <p className="mt-2 text-bee-muted">
        Some steps are reconstructed from our general guide. If your provider&apos;s menus differ, your
        BeeKeeper can confirm the exact path.
      </p>
    </div>
  );
}
