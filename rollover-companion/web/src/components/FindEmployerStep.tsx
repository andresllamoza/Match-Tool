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
  const content = (
    <>
        <ProgressSteps current="find" variant="minimal" />

        <h1
          className={`mb-2 font-bold tracking-tight text-bee-charcoal ${
            embedded ? "text-3xl" : "text-3xl sm:text-4xl"
          }`}
        >
          Find your old 401(k)
        </h1>
        <p className="mb-6 text-base leading-relaxed text-[#555555]">
          Tell us your former employer or plan provider. We&apos;ll handle the lookup to locate
          your exact routing details.
        </p>

        <label htmlFor="employer-find" className="mb-2 block text-sm font-semibold text-bee-charcoal">
          Former employer
        </label>
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
          placeholder="e.g. Google, Target, FedEx"
          disabled={loading}
          className="mb-4 h-14 w-full rounded-xl border border-bee-border bg-white px-4 text-lg text-bee-charcoal shadow-none outline-none transition-all placeholder:text-bee-muted/70 hover:border-bee-charcoal focus:border-2 focus:border-bee-charcoal focus:ring-0 disabled:opacity-50"
        />

        <Button
          onClick={onSearch}
          disabled={loading}
          className="mb-4 h-14 min-h-[56px] rounded-xl bg-bee-charcoal text-base font-semibold text-white active:scale-[0.99] transition-transform duration-100"
        >
          {searchLabel}
        </Button>

        <div className="space-y-2 border-t border-bee-border pt-4">
          {showKnowProvider && (
            <button
              type="button"
              onClick={onKnowProvider}
              disabled={loading}
              className="block w-full text-left text-sm font-semibold text-bee-muted transition-colors hover:text-bee-charcoal disabled:opacity-50"
            >
              I already know my 401(k) provider →
            </button>
          )}
          <button
            type="button"
            onClick={onAskQuestion}
            disabled={loading}
            className="block w-full text-left text-sm font-semibold text-bee-muted transition-colors hover:text-bee-charcoal disabled:opacity-50"
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
        {showPerk && (
          <div className="mt-6 rounded-xl border border-[#EAE5DC] bg-[#FFF9E6] p-5">
            <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
              PensionBee perk
            </p>
            <p className="mt-1 text-sm font-semibold leading-relaxed text-[#111111]">
              Roll your old 401(k) to PensionBee and get a 1% match on eligible transfers.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mx-auto mt-8 w-full max-w-lg text-left">
      <div className="rounded-2xl border border-bee-border bg-white p-8 shadow-sm">{content}</div>
      {showPerk && (
        <div className="mt-4 rounded-xl border border-bee-border bg-[#FFF9E6] p-5">
          <p className="text-xs font-bold uppercase tracking-wider text-bee-muted">PensionBee perk</p>
          <p className="mt-1 text-sm font-semibold leading-relaxed text-bee-charcoal">
            Roll your old 401(k) to PensionBee and get a 1% match on eligible transfers.
          </p>
        </div>
      )}
    </div>
  );
}
