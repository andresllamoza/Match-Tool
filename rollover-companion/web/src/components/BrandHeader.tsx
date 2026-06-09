import Link from "next/link";

interface BrandHeaderProps {
  mode?: "customer" | "agent" | "embed";
  compact?: boolean;
}

export function BrandHeader({ mode = "customer", compact = false }: BrandHeaderProps) {
  return (
    <header
      className={`flex items-center justify-between ${compact ? "mb-4" : "mb-6 lg:mb-8"}`}
    >
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-bee-yellow text-lg font-bold text-bee-ink lg:h-12 lg:w-12 lg:text-xl">
          🐝
        </div>
        <div>
          <p className="text-lg font-bold text-bee-blue lg:text-xl">PensionBee</p>
          {!compact && (
            <p className="text-sm text-bee-muted lg:text-base">Rollover Companion</p>
          )}
        </div>
      </div>
      {mode !== "embed" && (
        <nav className="hidden items-center gap-4 text-sm font-medium text-bee-muted md:flex">
          <Link href="/customer" className="hover:text-bee-blue">
            Customer
          </Link>
          <Link href="/agent" className="hover:text-bee-blue">
            Agent
          </Link>
          <Link href="/funnel" className="hover:text-bee-blue">
            Funnel
          </Link>
          <Link href="/embed" className="hover:text-bee-blue">
            Embed
          </Link>
        </nav>
      )}
      {mode === "agent" && (
        <span className="rounded-pill bg-bee-blue px-3 py-1 text-xs font-semibold text-white md:hidden">
          Agent
        </span>
      )}
    </header>
  );
}
