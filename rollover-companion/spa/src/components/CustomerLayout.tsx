import { Link } from "react-router-dom";

export function CustomerLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto min-h-dvh max-w-customer px-5 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-bee text-lg">🐝</span>
          <span className="text-lg font-bold tracking-tight text-ink">PensionBee</span>
        </div>
        <Link to="/agent" className="text-xs font-semibold text-muted hover:text-ink">
          Agent view
        </Link>
      </header>
      {children}
    </div>
  );
}
