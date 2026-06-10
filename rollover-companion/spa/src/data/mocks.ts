import type { ProviderMock } from "../types/journey";

export const PENSIONBEE_MAIL = "PO Box 72, New York, NY 10272";

export const PROVIDERS: Record<string, ProviderMock> = {
  fidelity: {
    id: "fidelity",
    name: "Fidelity",
    onlineSteps: [
      "Log in to NetBenefits and open your 401(k).",
      "Choose Withdrawals or Take money out.",
      "Select Rollover to another retirement account (not cash).",
      "Pick Express rollover if you see it — it's usually fastest.",
      "Enter PensionBee as the receiving IRA provider.",
      "Confirm pre-tax funds go to your Traditional IRA.",
      "Submit and save your confirmation number.",
    ],
    phoneScript: {
      opening: "I'd like to request a direct rollover from my 401(k) to an external IRA at PensionBee.",
      qa: [
        { theyAsk: "Pre-tax or Roth?", youSay: "Pre-tax to a Traditional IRA." },
        { theyAsk: "Where should we send the check?", youSay: "Mail to PensionBee at PO Box 72, New York, NY 10272." },
        { theyAsk: "How should the check be payable?", youSay: "PensionBee FBO [your name] — spelled exactly." },
      ],
    },
    formSteps: [
      "Check the box for direct rollover to another retirement account.",
      "Write PensionBee FBO [your name] in the payee field.",
      "Use PO Box 72, New York, NY 10272 as the mailing address.",
    ],
    onlineDays: "2–5 business days",
    checkDays: "7–10 business days",
    mailToUser: false,
    expressRollover: true,
  },
  empower: {
    id: "empower",
    name: "Empower",
    onlineSteps: [
      "Sign in to the Empower participant portal.",
      "Open Distributions or Withdrawals.",
      "Choose rollover to another provider.",
      "Enter PensionBee as the destination IRA.",
      "Confirm your home address — Empower mails the check to you first.",
      "Request the check payable to PensionBee FBO [your name].",
      "We'll send a prepaid envelope to forward it to PensionBee.",
    ],
    phoneScript: {
      opening: "I'm calling to start a direct rollover from my Empower 401(k) to PensionBee.",
      qa: [
        { theyAsk: "Pre-tax or Roth?", youSay: "Pre-tax to Traditional IRA." },
        { theyAsk: "Mailing address?", youSay: "My address on file — I'll forward to PensionBee." },
        { theyAsk: "Payable to?", youSay: "PensionBee FBO [your name]." },
      ],
    },
    formSteps: [
      "Select direct rollover.",
      "Payee: PensionBee FBO [your name].",
      "Mail to your home address on file.",
    ],
    onlineDays: "7–10 business days",
    checkDays: "7–10 business days",
    mailToUser: true,
    notaryEdgeCase: "Some Empower plans require notarization — your BeeKeeper can arrange virtual notary support.",
  },
  alight: {
    id: "alight",
    name: "Alight Solutions",
    onlineSteps: [
      "Go to alight.com/find-your-hr-website and open your employer's benefits site.",
      "Log in and open Savings & Retirement.",
      "Choose Rollover or Move money out.",
      "Select RolloverCentral and start a direct rollover.",
      "Search for PensionBee and link your account with your 14-digit VAN from BeeHive.",
      "Confirm pre-tax funds go to your Traditional IRA.",
      "Submit and save your confirmation.",
    ],
    phoneScript: {
      opening: "I'd like a direct rollover from my Alight 401(k) to PensionBee.",
      qa: [
        { theyAsk: "Pre-tax or Roth?", youSay: "Pre-tax to Traditional IRA." },
        { theyAsk: "Check payable?", youSay: "PensionBee FBO [your name]." },
        { theyAsk: "Mailing address?", youSay: "PO Box 72, New York, NY 10272." },
      ],
    },
    formSteps: [
      "Direct rollover to external IRA.",
      "Payee: PensionBee FBO [your name].",
      "Mail: PO Box 72, New York, NY 10272.",
    ],
    onlineDays: "2–3 business days",
    checkDays: "up to 2 weeks by check",
    mailToUser: false,
  },
  vanguard: {
    id: "vanguard",
    name: "Vanguard",
    onlineSteps: [
      "Log in to your Vanguard account.",
      "Navigate to Rollovers or Distributions.",
      "Choose direct rollover to an external IRA.",
      "Enter PensionBee as receiving provider.",
      "Use PensionBee FBO [your name] as payee.",
      "Mail to PO Box 72, New York, NY 10272.",
      "Submit the request.",
    ],
    phoneScript: {
      opening: "I need a direct rollover from my Vanguard 401(k) to PensionBee.",
      qa: [
        { theyAsk: "Account type?", youSay: "Traditional IRA at PensionBee." },
        { theyAsk: "Check payable?", youSay: "PensionBee FBO [your name]." },
      ],
    },
    formSteps: ["Direct rollover", "Payee: PensionBee FBO [your name]", "Mail: PO Box 72, NY 10272"],
    onlineDays: "7–10 business days",
    checkDays: "7–10 business days",
    mailToUser: false,
  },
  voya: {
    id: "voya",
    name: "Voya",
    onlineSteps: [
      "Log in to the Voya participant site.",
      "Open Withdrawals / Rollovers.",
      "Select rollover to another retirement account.",
      "Destination: PensionBee IRA.",
      "Payable: PensionBee FBO [your name].",
      "Mail to PO Box 72, New York, NY 10272.",
      "Complete phone verification if prompted.",
    ],
    phoneScript: {
      opening: "I'd like a direct rollover from my Voya 401(k) to PensionBee.",
      qa: [
        { theyAsk: "Verification?", youSay: "I can complete phone verification now." },
        { theyAsk: "Payable line?", youSay: "PensionBee FBO [your name]." },
      ],
    },
    formSteps: ["Rollover election", "PensionBee FBO [your name]", "PO Box 72, NY 10272"],
    onlineDays: "7–10 business days",
    checkDays: "7–10 business days",
    mailToUser: false,
    phoneVerificationNote: "Voya may call to verify — keep your phone nearby.",
  },
  merrill: {
    id: "merrill",
    name: "Merrill Lynch",
    onlineSteps: ["BeeKeeper-guided rollover"],
    phoneScript: { opening: "", qa: [] },
    formSteps: [],
    onlineDays: "7–10 business days",
    checkDays: "7–10 business days",
    mailToUser: false,
  },
};

export interface LookupResult {
  providerId?: string;
  providerName?: string;
  matchedEmployer: string;
  confidence: "high" | "low" | "not_covered";
  disambiguation?: { question: string; options: [string, string] };
}

export function mockLookup(employer: string): LookupResult {
  const q = employer.trim().toLowerCase();
  if (q.includes("amazon")) {
    return { providerId: "fidelity", providerName: "Fidelity", matchedEmployer: "Amazon.com Services LLC", confidence: "high" };
  }
  if (q.includes("citi") || q.includes("citigroup")) {
    return {
      providerId: "alight",
      providerName: "Alight Solutions",
      matchedEmployer: "Citigroup Inc.",
      confidence: "high",
    };
  }
  if (q.includes("dollar tree") || (q === "apple" || q.includes("apple inc"))) {
    const name = q.includes("dollar") ? "Dollar Tree, Inc." : "Apple Inc.";
    return { providerId: "empower", providerName: "Empower", matchedEmployer: name, confidence: "high" };
  }
  if (q.includes("cardinal")) {
    return {
      matchedEmployer: employer.trim(),
      confidence: "low",
      disambiguation: {
        question: "Which plan sounds right?",
        options: ["Cardinal Health 401(k) — Empower", "Cardinal Micro Devices Inc. — Vanguard"],
      },
    };
  }
  if (q.includes("walmart")) {
    return { providerId: "merrill", providerName: "Merrill Lynch", matchedEmployer: "Walmart Inc.", confidence: "not_covered" };
  }
  if (q.includes("voya")) {
    return { providerId: "voya", providerName: "Voya", matchedEmployer: employer.trim(), confidence: "high" };
  }
  if (q.includes("vanguard")) {
    return { providerId: "vanguard", providerName: "Vanguard", matchedEmployer: employer.trim(), confidence: "high" };
  }
  if (q.includes("home depot") || q.includes("marriott") || q.includes("rtx")) {
    return {
      providerId: "alight",
      providerName: "Alight Solutions",
      matchedEmployer: employer.trim(),
      confidence: "high",
    };
  }
  if (q.includes("fidelity") || q.includes("fedex") || q.includes("target")) {
    return { providerId: "fidelity", providerName: "Fidelity", matchedEmployer: employer.trim(), confidence: "high" };
  }
  return {
    matchedEmployer: employer.trim(),
    confidence: "low",
    disambiguation: {
      question: "We found more than one match — which employer is yours?",
      options: [`${employer.trim()} — Fidelity plan`, `${employer.trim()} — Alight plan`],
    },
  };
}

export function resolveDisambiguation(answer: string): LookupResult {
  const lower = answer.toLowerCase();
  if (lower.includes("empower")) {
    return { providerId: "empower", providerName: "Empower", matchedEmployer: answer.split("—")[0]?.trim() || answer, confidence: "high" };
  }
  if (lower.includes("vanguard")) {
    return { providerId: "vanguard", providerName: "Vanguard", matchedEmployer: answer.split("—")[0]?.trim() || answer, confidence: "high" };
  }
  if (lower.includes("alight")) {
    return { providerId: "alight", providerName: "Alight Solutions", matchedEmployer: answer.split("—")[0]?.trim() || answer, confidence: "high" };
  }
  return { providerId: "fidelity", providerName: "Fidelity", matchedEmployer: answer.split("—")[0]?.trim() || answer, confidence: "high" };
}
