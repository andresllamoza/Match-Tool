"use client";

import { Button } from "./ui/Button";
import { ProgressSteps } from "./ProgressSteps";

interface FindEmployerStepProps {
  employer: string;
  onEmployerChange: (value: string) => void;
  onSearch: () => void;
  onKnowProvider: () => void;
  onAskQuestion: () => void;
  searchLabel: string;
  loading?: boolean;
  showKnowProvider?: boolean;
  showPerk?: boolean;
  /** Inside sandbox/parent card — no nested white shell */
  embedded?: boolean;
}

function SearchIcon() {
  return (
    <svg
      className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-bee-muted"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
      aria-hidden
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 21l-4.35-4.35M11 18a7 7 0 100-14 7 7 0 000 14z"
      />
    </svg>
  );
}

function PerkCoinIcon() {
  return (
    <div
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-bee-yellow text-sm font-extrabold text-bee-charcoal"
      aria-hidden
    >
      1%
    </div>
  );
}

export function FindEmployerStep({
  employer,
  onEmployerChange,
  onSearch,
  onKnowProvider,
  onAskQuestion,
  searchLabel,
  loading,
  showKnowProvider,
  showPerk,
  embedded = false,
}: FindEmployerStepProps) {
  const perkCard = showPerk ? (
    <div className="mt-6 flex gap-4 rounded-block border border-bee-border bg-bee-yellow-tint p-5">
      <PerkCoinIcon />
      <div>
        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
          PensionBee perk
        </p>
        <p className="mt-1 text-sm font-semibold leading-relaxed text-bee-charcoal">
          Roll your old 401(k) to PensionBee and get a 1% match on eligible transfers.
        </p>
      </div>
    </div>
  ) : null;

  const content = (
    <>
      <ProgressSteps current="find" variant="minimal" />

      <span className="mb-3 block text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
        Step 1 · Find
      </span>

      <h1
        className={`mb-6 font-extrabold leading-[1.1] tracking-[-0.03em] text-bee-charcoal ${
          embedded ? "text-4xl" : "text-4xl sm:text-5xl"
        }`}
      >
        Find your old 401(k)
      </h1>

      <p className="mb-8 max-w-xl text-lg leading-relaxed text-bee-muted">
        Tell us your former employer. We&apos;ll find which company holds your plan (like Fidelity or
        Vanguard) and pull your exact routing details.
      </p>

      <label htmlFor="employer-find" className="mb-2 block text-sm font-semibold text-bee-charcoal">
        Former employer
      </label>
      <div className="relative mb-2">
        <SearchIcon />
        <input
          id="employer-find"
          value={employer}
          onChange={(e) => onEmployerChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !loading) {
              e.preventDefault();
              onSearch();
            }
          }}
          placeholder="e.g. Google, Target, FedEx, Amazon"
          disabled={loading}
          aria-describedby="employer-find-helper"
          className="h-14 min-h-[56px] w-full rounded-input border-2 border-bee-border bg-white pl-12 pr-5 text-lg text-bee-ink shadow-sm outline-none transition-colors placeholder:text-bee-faint/80 hover:border-bee-charcoal/20 focus:border-bee-yellow focus:ring-2 focus:ring-bee-yellow/25 disabled:opacity-50"
        />
      </div>
      <p id="employer-find-helper" className="mb-6 text-sm leading-relaxed text-bee-muted">
        We only use your employer name to find which company holds your old 401(k) — never to sell
        your data.
      </p>

      <Button onClick={onSearch} disabled={loading} className="mb-6">
        {searchLabel}
      </Button>

      <div className="space-y-1 border-t border-bee-border pt-4">
        {showKnowProvider && (
          <button
            type="button"
            onClick={onKnowProvider}
            disabled={loading}
            className="pb-text-link justify-start text-left"
          >
            I already know my 401(k) provider →
          </button>
        )}
        <button
          type="button"
          onClick={onAskQuestion}
          disabled={loading}
          className="pb-text-link justify-start text-left"
        >
          Ask a question about this step →
        </button>
      </div>
    </>
  );

  if (embedded) {
    return (
      <div className="w-full text-left">
        {content}
        {perkCard}
      </div>
    );
  }

  return (
    <div className="mx-auto mt-8 w-full max-w-lg text-left">
      <div className="rounded-card border border-bee-border bg-white p-8 shadow-sm">{content}</div>
      {perkCard}
    </div>
  );
}
