export function SourceStatusBadge({
  status,
}: {
  status: "verified" | "reconstructed" | null | undefined;
}) {
  if (!status) return null;

  if (status === "verified") {
    return (
      <span className="inline-flex items-center gap-1 rounded-lg border border-[#EAE5DC] bg-white px-3 py-1.5 text-xs font-semibold text-[#1B7F4B] shadow-sm lg:text-sm">
        <span aria-hidden>✓</span> Verified path
      </span>
    );
  }

  return (
    <div className="rounded-xl border border-amber-300/70 bg-amber-50/90 px-5 py-4 text-sm leading-relaxed text-amber-950 shadow-sm lg:text-base">
      <p className="flex items-center gap-2 font-semibold">
        <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-amber-200 text-xs" aria-hidden>
          !
        </span>
        Human verification recommended
      </p>
      <p className="mt-2 text-amber-900/90">
        Some steps are reconstructed from our general guide. If your provider&apos;s menus differ, your
        BeeKeeper can confirm the exact path.
      </p>
    </div>
  );
}
