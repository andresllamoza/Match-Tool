export const DEMO_PROVIDERS = [
  "Fidelity",
  "Vanguard",
  "Empower",
  "Merrill Lynch",
  "Alight",
  "Principal",
  "Voya",
] as const;

export const PAYEE_TEMPLATE = "PensionBee FBO [your name]";
export const MAILING = "PO Box 72, New York, NY 10272";
export const DESTINATION = "PensionBee IRA";

const EMPLOYER_HINTS: [string, string][] = [
  ["target", "Alight"],
  ["walmart", "Merrill Lynch"],
  ["amazon", "Fidelity"],
  ["google", "Fidelity"],
  ["alphabet", "Fidelity"],
  ["fedex", "Vanguard"],
  ["apple", "Fidelity"],
  ["microsoft", "Fidelity"],
];

export function resolveProvider(employer: string): string {
  const lower = employer.toLowerCase();
  for (const [hint, provider] of EMPLOYER_HINTS) {
    if (lower.includes(hint)) return provider;
  }
  return "Fidelity";
}

export const PHONE_BY_PROVIDER: Record<string, string> = {
  Fidelity: "800-343-3548",
  Vanguard: "800-523-1188",
  Empower: "800-338-4015",
  "Merrill Lynch": "800-895-7164",
  Alight: "800-279-4030",
  Principal: "800-547-7754",
  Voya: "800-584-6001",
};
