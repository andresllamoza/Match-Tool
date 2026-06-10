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
    <div className="rounded-2xl border border-[#EAE5DC] border-l-4 border-l-[#FFC72C] bg-white p-8 shadow-sm sm:p-10">
      {intro && (
        <p className="mb-4 text-sm leading-relaxed text-[#555555]">{intro}</p>
      )}
      <p className="text-xs font-bold uppercase tracking-wider text-[#6B6560]">
        {channel === "forms" && fieldLabel ? fieldLabel : LABELS[channel]}
      </p>
      <p className="mt-3 text-lg font-semibold leading-relaxed text-[#1E242B] sm:text-xl">
        {channel === "phone" ? `\u201C${script}\u201D` : script}
      </p>
    </div>
  );
}
