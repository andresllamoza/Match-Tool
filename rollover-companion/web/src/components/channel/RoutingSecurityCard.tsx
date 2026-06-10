import { isFboPayableLine } from "@/lib/checkPayable";
import { CopyMicroButton } from "./CopyMicroButton";

function SecurityFieldRow({
  label,
  value,
  prominent = false,
}: {
  label: string;
  value: string;
  prominent?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 px-6 py-5 sm:px-8 sm:py-6">
      <div className="min-w-0 flex-1">
        <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
          {label}
        </p>
        <p
          className={`mt-2 break-words leading-snug text-[#1E242B] ${
            prominent
              ? "text-xl font-bold tracking-tight sm:text-2xl"
              : "text-base font-semibold sm:text-lg"
          }`}
        >
          {value}
        </p>
      </div>
      <CopyMicroButton value={value} label={label} />
    </div>
  );
}

export function RoutingSecurityCard({
  payeeLine,
  mailingAddress,
}: {
  payeeLine?: string;
  mailingAddress?: string;
}) {
  const hasPayee = Boolean(payeeLine);
  const hasMail = Boolean(mailingAddress);
  const showFbo = payeeLine ? isFboPayableLine(payeeLine) : false;

  if (!hasPayee && !hasMail) return null;

  return (
    <div role="region" aria-label="Check routing security">
      {showFbo && (
        <div className="mb-4 flex items-start gap-3 sm:mb-5">
          <span
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#111111] text-base text-white"
            aria-hidden
          >
            🔒
          </span>
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-[#9A6200]">
              Critical — check payable to
            </p>
            <p className="mt-1 text-sm leading-relaxed text-[#555555]">
              Use these exact details or your rollover may be rejected.
            </p>
          </div>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-[#EAE5DC] bg-[#FDFDFD] divide-y divide-[#F0E6D2] shadow-sm">
        {hasPayee && (
          <SecurityFieldRow
            label={showFbo ? "Check payable to" : "Payee name"}
            value={payeeLine!}
            prominent={showFbo}
          />
        )}
        {hasMail && (
          <SecurityFieldRow label="Mailing address" value={mailingAddress!} />
        )}
      </div>
    </div>
  );
}
