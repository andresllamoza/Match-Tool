"use client";

export function DemoPreviewBanner() {
  if (process.env.NEXT_PUBLIC_DEMO_MODE !== "true") return null;

  return (
    <div
      className="border-b border-bee-yellow/30 bg-bee-yellow-tint/80 px-4 py-2.5 text-center backdrop-blur-sm"
      role="status"
    >
      <p className="text-xs font-semibold tracking-wide text-bee-ink sm:text-sm">
        Interactive preview with guided demo data — fully clickable end-to-end
      </p>
    </div>
  );
}
