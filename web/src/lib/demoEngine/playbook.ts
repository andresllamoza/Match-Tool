import { PLAYBOOK_DATA } from "./playbookSteps";

export type DemoChannel = "online" | "phone" | "forms";

type ProviderPlaybook = (typeof PLAYBOOK_DATA.providers)[keyof typeof PLAYBOOK_DATA.providers];

function canonicalProvider(provider: string | null | undefined): string {
  if (!provider) return "Fidelity";
  const alias = PLAYBOOK_DATA.demoAliases[provider as keyof typeof PLAYBOOK_DATA.demoAliases];
  if (alias) return alias;
  if (provider in PLAYBOOK_DATA.providers) return provider;
  return "Fidelity";
}

function providerPlaybook(provider: string | null | undefined): ProviderPlaybook {
  const key = canonicalProvider(provider);
  return (
    PLAYBOOK_DATA.providers[key as keyof typeof PLAYBOOK_DATA.providers] ??
    PLAYBOOK_DATA.providers.Fidelity
  );
}

/** Portal menu hints only for uncovered providers — matches live API general_path behavior. */
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

export function channelStepCount(provider: string | null | undefined, channel: DemoChannel): number {
  const pb = providerPlaybook(provider);
  if (channel === "online") return pb.online.length || PLAYBOOK_DATA.general.online.length;
  if (channel === "phone") return pb.phone.length || PLAYBOOK_DATA.general.phone.length;
  return pb.forms.length || PLAYBOOK_DATA.general.forms.length;
}

export function providerPortalName(provider: string | null | undefined): string | null {
  const portal = providerPlaybook(provider).portal?.trim();
  return portal || null;
}

export function providerMechanism(provider: string | null | undefined): string | null {
  return providerPlaybook(provider).mechanism || null;
}

export function providerCheckDestination(provider: string | null | undefined): string | null {
  return providerPlaybook(provider).checkDestination || null;
}

export function channelStepContent(
  provider: string | null | undefined,
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
  const pb = providerPlaybook(provider);
  const general = PLAYBOOK_DATA.general;
  const useGeneralHints = !pb.online.length;

  if (channel === "online") {
    const steps = pb.online.length ? pb.online : general.online;
    const sayThis = steps[Math.min(stepIndex, steps.length - 1)] ?? steps[0] ?? "";
    const hints = hintsForStep(sayThis, useGeneralHints);
    return {
      sayThis,
      stepLabel: `Step ${stepIndex + 1}`,
      phoneIntro: null,
      repQuestions: [],
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
    const steps = pb.phone.length ? pb.phone : general.phone;
    const sayThis = steps[Math.min(stepIndex, steps.length - 1)] ?? steps[0] ?? "";
    return {
      sayThis,
      stepLabel: `Step ${stepIndex + 1}`,
      phoneIntro: stepIndex === 0 ? pb.phoneIntro || "When the representative answers, say:" : null,
      repQuestions: [...pb.repQuestions],
      portalMenuHints: [],
      destinationHints: [],
      forwardStepRequired: pb.forwardStepRequired,
      hasReconstructed: false,
      portalName: pb.portal || null,
      mechanism: pb.mechanism || null,
      checkDestination: pb.checkDestination || null,
    };
  }

  const fields = pb.forms.length ? pb.forms : general.forms;
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
