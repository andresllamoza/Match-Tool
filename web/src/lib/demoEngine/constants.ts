import { isProviderInLibrary } from "./playbook";

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

/** Employers that match a recordkeeper not yet in the provider guide library. */
const UNCOVERED_HINTS: [string, string][] = [
  ["uncovered demo", "Paychex"],
  ["five below", "Paychex"],
];

export function resolveLookup(employer: string): {
  provider: string | null;
  uncoveredProvider: string | null;
} {
  const lower = employer.toLowerCase();
  for (const [hint, recordkeeper] of [...EMPLOYER_HINTS, ...UNCOVERED_HINTS]) {
    if (lower.includes(hint)) {
      if (isProviderInLibrary(recordkeeper)) {
        return { provider: recordkeeper, uncoveredProvider: null };
      }
      return { provider: null, uncoveredProvider: recordkeeper };
    }
  }
  return { provider: null, uncoveredProvider: "your 401(k) provider" };
}

/** @deprecated Prefer resolveLookup — returns the matched or uncovered recordkeeper label. */
export function resolveProvider(employer: string): string {
  const { provider, uncoveredProvider } = resolveLookup(employer);
  return provider || uncoveredProvider || "your 401(k) provider";
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
