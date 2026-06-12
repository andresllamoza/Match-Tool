import { PLAYBOOK_DATA } from "./playbookSteps";

export type DemoChannel = "online" | "phone" | "forms";

interface PlaybookEntry {
  isGeneral: boolean;
  online: readonly string[];
  phoneSteps: readonly string[];
  forms: readonly { label: string; instruction: string }[];
  portal: string;
  preferredPath: string;
  phoneNumber: string;
  phoneIntro: string;
  mechanism: string;
  checkDestination: string;
  providerIdentifiedMessage: string;
  accessPortalName: string;
  accessResetSteps: readonly string[];
  lockoutPhone: string;
  lockoutScript: string;
  repQuestions: readonly { question: string; answer: string }[];
  forwardStepRequired: boolean;
  hasReconstructed: boolean;
  rolloverInitiatedMessage?: string;
  inFlightMessage?: string;
  completeMessage?: string;
}

function asPlaybookEntry(
  raw: typeof PLAYBOOK_DATA.general | (typeof PLAYBOOK_DATA.providers)[keyof typeof PLAYBOOK_DATA.providers],
  isGeneral: boolean
): PlaybookEntry {
  return { ...(raw as unknown as Omit<PlaybookEntry, "isGeneral">), isGeneral };
}

function canonicalKey(provider: string): string {
  const alias = PLAYBOOK_DATA.demoAliases[provider as keyof typeof PLAYBOOK_DATA.demoAliases];
  return alias || provider;
}

export function isProviderInLibrary(provider: string | null | undefined): boolean {
  if (!provider) return false;
  return canonicalKey(provider) in PLAYBOOK_DATA.providers;
}

function generalEntry(): PlaybookEntry {
  return asPlaybookEntry(PLAYBOOK_DATA.general, true);
}

function providerEntry(provider: string): PlaybookEntry {
  const key = canonicalKey(provider);
  const pb = PLAYBOOK_DATA.providers[key as keyof typeof PLAYBOOK_DATA.providers];
  if (!pb) return generalEntry();
  return asPlaybookEntry(pb, false);
}

/** Resolve guide for a covered provider name or general guide for uncovered recordkeepers. */
export function resolvePlaybook(recordkeeper: string | null | undefined): PlaybookEntry {
  if (!recordkeeper) return generalEntry();
  if (isProviderInLibrary(recordkeeper)) return providerEntry(recordkeeper);
  return generalEntry();
}

function hintsForStep(text: string, useGeneralHints: boolean): { portal: string[]; destination: string[] } {
  if (!useGeneralHints) {
    return { portal: [], destination: [] };
  }
  const lower = text.toLowerCase();
  const portal =
    ["withdrawal", "rollover", "distribution", "transfer"].some((w) => lower.includes(w))
      ? [...PLAYBOOK_DATA.portalMenuHints]
      : [];
  const destination =
    ["other", "pensionbee", "not listed", "provider"].some((w) => lower.includes(w))
      ? [...PLAYBOOK_DATA.destinationHints]
      : [];
  return { portal, destination };
}

export function channelStepCount(recordkeeper: string | null | undefined, channel: DemoChannel): number {
  const pb = resolvePlaybook(recordkeeper);
  if (channel === "online") return pb.online.length;
  if (channel === "phone") return pb.phoneSteps.length;
  return pb.forms.length;
}

export function providerPortalName(recordkeeper: string | null | undefined): string | null {
  const portal = resolvePlaybook(recordkeeper).portal?.trim();
  return portal || null;
}

export function providerGuideInfo(recordkeeper: string | null | undefined) {
  const pb = resolvePlaybook(recordkeeper);
  return {
    isGeneral: pb.isGeneral,
    preferredPath: pb.preferredPath || null,
    portal: pb.portal || null,
    phone: pb.phoneNumber || null,
    mechanism: pb.mechanism || null,
    checkDestination: pb.checkDestination || null,
    forwardStepRequired: pb.forwardStepRequired,
    providerIdentifiedMessage: pb.providerIdentifiedMessage || null,
    accessPortalName: pb.accessPortalName || pb.portal || null,
    accessResetSteps: pb.accessResetSteps || [],
    lockoutPhone: pb.lockoutPhone || null,
    lockoutScript: pb.lockoutScript || null,
    rolloverInitiatedMessage:
      ("rolloverInitiatedMessage" in pb && pb.rolloverInitiatedMessage
        ? String(pb.rolloverInitiatedMessage)
        : null) || PLAYBOOK_DATA.general.rolloverInitiatedMessage || null,
    inFlightMessage:
      ("inFlightMessage" in pb && pb.inFlightMessage ? String(pb.inFlightMessage) : null) ||
      PLAYBOOK_DATA.general.inFlightMessage ||
      null,
    completeMessage:
      ("completeMessage" in pb && pb.completeMessage ? String(pb.completeMessage) : null) ||
      PLAYBOOK_DATA.general.completeMessage ||
      null,
    repQuestions: [...pb.repQuestions],
  };
}

export function channelStepContent(
  recordkeeper: string | null | undefined,
  channel: DemoChannel,
  stepIndex: number
): {
  sayThis: string;
  stepLabel: string;
  phoneIntro: string | null;
  repQuestions: { question: string; answer: string }[];
  portalMenuHints: string[];
  destinationHints: string[];
  forwardStepRequired: boolean;
  hasReconstructed: boolean;
  portalName: string | null;
  mechanism: string | null;
  checkDestination: string | null;
} {
  const pb = resolvePlaybook(recordkeeper);
  const useGeneralHints = pb.isGeneral;

  if (channel === "online") {
    const steps = pb.online;
    const sayThis = steps[Math.min(stepIndex, steps.length - 1)] ?? steps[0] ?? "";
    const hints = hintsForStep(sayThis, useGeneralHints);
    return {
      sayThis,
      stepLabel: `Step ${stepIndex + 1}`,
      phoneIntro: null,
      repQuestions: useGeneralHints ? [...pb.repQuestions] : [],
      portalMenuHints: hints.portal,
      destinationHints: hints.destination,
      forwardStepRequired: pb.forwardStepRequired,
      hasReconstructed: pb.hasReconstructed,
      portalName: pb.portal || null,
      mechanism: pb.mechanism || null,
      checkDestination: pb.checkDestination || null,
    };
  }

  if (channel === "phone") {
    const steps = pb.phoneSteps;
    const sayThis = steps[Math.min(stepIndex, steps.length - 1)] ?? steps[0] ?? "";
    const hints = hintsForStep(sayThis, useGeneralHints);
    return {
      sayThis,
      stepLabel: `Step ${stepIndex + 1}`,
      phoneIntro: stepIndex === 0 ? pb.phoneIntro || null : null,
      repQuestions: [...pb.repQuestions],
      portalMenuHints: hints.portal,
      destinationHints: hints.destination,
      forwardStepRequired: pb.forwardStepRequired,
      hasReconstructed: false,
      portalName: pb.portal || null,
      mechanism: pb.mechanism || null,
      checkDestination: pb.checkDestination || null,
    };
  }

  const fields = pb.forms;
  const field = fields[Math.min(stepIndex, fields.length - 1)] ?? fields[0];
  return {
    sayThis: field?.instruction ?? "",
    stepLabel: field?.label ?? `Step ${stepIndex + 1}`,
    phoneIntro: null,
    repQuestions: [],
    portalMenuHints: [],
    destinationHints: [],
    forwardStepRequired: pb.forwardStepRequired,
    hasReconstructed: false,
    portalName: pb.portal || null,
    mechanism: pb.mechanism || null,
    checkDestination: pb.checkDestination || null,
  };
}
