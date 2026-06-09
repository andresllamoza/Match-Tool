export function SourceStatusBadge({
  status,
}: {
  status: "verified" | "reconstructed" | null | undefined;
}) {
  if (!status) return null;

  if (status === "verified") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-pill bg-bee-green-soft px-3 py-1 text-xs font-semibold text-bee-green lg:text-sm">
        ✓ Verified Transfer Path
      </span>
    );
  }

  return (
    <div className="rounded-card border-2 border-amber-400/80 bg-amber-50/80 px-4 py-3 text-sm leading-relaxed text-amber-950 lg:text-base">
      <p className="font-semibold">Double-check this layout</p>
      <p className="mt-1 text-amber-900/90">
        If your old provider&apos;s automated phone menu options look different, let your BeeKeeper
        know.
      </p>
    </div>
  );
}
