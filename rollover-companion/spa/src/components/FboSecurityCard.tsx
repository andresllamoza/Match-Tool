import { CopyButton } from "./CopyButton";

export function FboSecurityCard({
  payee,
  mailTo,
}: {
  payee: string;
  mailTo: string;
}) {
  return (
    <div className="my-6">
      <div className="rounded-2xl border-2 border-ink bg-white p-6">
        <p className="text-[11px] font-extrabold uppercase tracking-widest text-ink">
          Make the check payable to — exactly
        </p>
        <p className="mt-4 font-mono text-[clamp(1.1rem,4vw,1.35rem)] font-bold leading-snug text-ink">
          {payee}
        </p>
        <div className="mt-5 flex items-start justify-between gap-4 border-t border-border pt-5">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-muted">Mail to</p>
            <p className="mt-1 text-[17px] font-semibold leading-snug text-ink">{mailTo}</p>
          </div>
          <CopyButton value={`${payee}\n${mailTo}`} />
        </div>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-muted">
        If a check ever arrives payable to you personally, don&apos;t cash it — that&apos;s a
        withdrawal, not a rollover. Your BeeKeeper will fix it.
      </p>
    </div>
  );
}
