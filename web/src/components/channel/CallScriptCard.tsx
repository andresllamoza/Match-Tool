"use client";

type ChannelKind = "phone" | "online" | "forms";

const LABELS: Record<ChannelKind, string> = {
  phone: "Say this",
  online: "Do this now",
  forms: "Fill in this field",
};

const CUSTOMER_INTROS: Record<ChannelKind, string | null> = {
  phone: "When speaking with your provider, use these exact phrases:",
  online: "Follow these steps in your provider portal:",
  forms: "Enter this on your distribution form:",
};

export function CallScriptCard({
  channel,
  script,
  fieldLabel,
  surface = "customer",
}: {
  channel: ChannelKind;
  script: string;
  fieldLabel?: string | null;
  surface?: "customer" | "agent" | "embed";
}) {
  const intro = surface === "customer" ? CUSTOMER_INTROS[channel] : null;

  return (
    <div className="rounded-block border-2 border-bee-yellow bg-white p-6 shadow-sm sm:p-8">
      {channel === "online" && (
        <span className="mb-3 inline-block rounded-pill bg-bee-charcoal px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-white">
          Do this
        </span>
      )}
      {intro && (
        <p className="mb-4 text-sm leading-relaxed text-bee-faint">{intro}</p>
      )}
      <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-bee-muted">
        {channel === "forms" && fieldLabel ? fieldLabel : LABELS[channel]}
      </p>
      <p className="mt-3 text-lg font-extrabold leading-relaxed text-bee-charcoal sm:text-xl">
        {channel === "phone" ? `\u201C${script}\u201D` : script}
      </p>
    </div>
  );
}
