"use client";

export function FloatingChatBubble({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="pb-interactive fixed bottom-24 right-4 z-40 flex h-[54px] w-[54px] items-center justify-center rounded-full bg-bee-charcoal shadow-card-lg hover:bg-bee-ink lg:bottom-8 lg:right-8"
      aria-label="Ask your BeeKeeper"
    >
      <svg className="h-6 w-6 text-bee-yellow" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
        <path d="M20 2H4a2 2 0 00-2 2v12a2 2 0 002 2h3l3.5 3.5a1 1 0 001.5-.8V18h8a2 2 0 002-2V4a2 2 0 00-2-2z" />
      </svg>
    </button>
  );
}
