export function BeeKeeperLink({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="mt-10 w-full py-2 text-center text-sm font-semibold text-muted hover:text-ink"
    >
      🐝 Talk to your BeeKeeper
    </button>
  );
}
