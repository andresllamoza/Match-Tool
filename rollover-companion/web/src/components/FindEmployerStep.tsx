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
          aria-describedby="employer-find-helper"
          className="mb-2 h-14 min-h-[56px] w-full rounded-xl border border-[#EAE5DC] bg-[#FFFFFF] px-5 text-lg text-[#1E242B] shadow-sm outline-none transition-all duration-200 placeholder:text-[#6B6560]/70 hover:border-[#111111]/30 focus:border-2 focus:border-[#FFC72C] focus:ring-2 focus:ring-[#FFC72C]/25 disabled:opacity-50"
        />
        <p id="employer-find-helper" className="mb-6 text-sm leading-relaxed text-[#6B6560]">
          We only use your employer name to match you to the correct 401(k) recordkeeper — never to
          sell your data.
        </p>

        <Button
          onClick={onSearch}
          disabled={loading}
          className="mb-6 h-14 min-h-[56px] rounded-xl"
        >
          {searchLabel}
        </Button>

        <div className="space-y-2 border-t border-bee-border pt-4">
          {showKnowProvider && (
            <button
              type="button"
              onClick={onKnowProvider}
              disabled={loading}
              className="pb-interactive block w-full py-2 text-left text-sm font-semibold text-[#6B6560] hover:text-[#1E242B] disabled:opacity-50"
            >
              I already know my 401(k) provider →
            </button>
          )}
          <button
            type="button"
            onClick={onAskQuestion}
            disabled={loading}
            className="pb-interactive block w-full py-2 text-left text-sm font-semibold text-[#6B6560] hover:text-[#1E242B] disabled:opacity-50"
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
