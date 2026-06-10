import { mockLookup, PROVIDERS, resolveDisambiguation } from "../data/mocks";
import type { JourneyAction, JourneyContext } from "../types/journey";

export const STORAGE_KEY = "pb_rollover_spa_v1";

export function initialContext(): JourneyContext {
  return {
    screen: "find",
    phase: "find",
    employerQuery: "",
    stepIndex: 0,
    stuckCount: 0,
    stuckOnStep: null,
    firstName: "",
    lastName: "",
    notCovered: false,
    welcomeBack: false,
    reconstructed: false,
    escalated: false,
  };
}

function applyLookup(ctx: JourneyContext, employer: string): JourneyContext {
  const result = mockLookup(employer);
  const next = { ...ctx, employerQuery: employer, matchedEmployer: result.matchedEmployer };
  if (result.confidence === "not_covered") {
    return {
      ...next,
      screen: "find_not_covered",
      phase: "find",
      providerId: result.providerId,
      providerName: result.providerName,
      notCovered: true,
    };
  }
  if (result.confidence === "low" && result.disambiguation) {
    return {
      ...next,
      screen: "find_disambiguate",
      phase: "find",
      disambiguation: result.disambiguation,
    };
  }
  return {
    ...next,
    screen: "find_success",
    phase: "find",
    providerId: result.providerId,
    providerName: result.providerName,
    notCovered: false,
  };
}

function totalSteps(ctx: JourneyContext): number {
  if (!ctx.providerId || !ctx.channel) return 0;
  const p = PROVIDERS[ctx.providerId];
  if (!p) return 0;
  if (ctx.channel === "online") return p.onlineSteps.length;
  if (ctx.channel === "phone") return p.phoneScript.qa.length + 1;
  return p.formSteps.length;
}

export function reduceJourney(ctx: JourneyContext, action: JourneyAction): JourneyContext {
  switch (action.type) {
    case "lookup":
      return applyLookup(ctx, action.employer);
    case "disambiguate": {
      const r = resolveDisambiguation(action.answer);
      return {
        ...ctx,
        screen: "find_success",
        phase: "find",
        providerId: r.providerId,
        providerName: r.providerName,
        matchedEmployer: r.matchedEmployer,
        disambiguation: undefined,
        notCovered: false,
      };
    }
    case "access":
      if (action.canLogin) {
        return { ...ctx, screen: "name", phase: "rollover", stepIndex: 0 };
      }
      return { ...ctx, screen: "access_recovery", phase: "access" };
    case "recovery_path":
      return { ...ctx, screen: "name", phase: "rollover" };
    case "set_name":
      return {
        ...ctx,
        firstName: action.firstName.trim(),
        lastName: action.lastName.trim(),
        screen: "tax",
      };
    case "set_tax":
      return { ...ctx, taxType: action.taxType, screen: "channel" };
    case "set_channel":
      return {
        ...ctx,
        channel: action.channel,
        screen: "channel_step",
        stepIndex: 0,
        stuckCount: 0,
        stuckOnStep: null,
      };
    case "step_done": {
      const total = totalSteps(ctx);
      const nextIndex = ctx.stepIndex + 1;
      if (nextIndex >= total) {
        return { ...ctx, screen: "track", phase: "track", stepIndex: 0 };
      }
      return { ...ctx, stepIndex: nextIndex, screen: "channel_step" };
    }
    case "step_stuck": {
      const sameStep = ctx.stuckOnStep === ctx.stepIndex;
      const count = sameStep ? ctx.stuckCount + 1 : 1;
      if (count >= 2) {
        return { ...ctx, screen: "escalated", phase: "track", escalated: true, stuckCount: count };
      }
      return {
        ...ctx,
        screen: "stuck",
        stuckCount: count,
        stuckOnStep: ctx.stepIndex,
      };
    }
    case "escalate":
      return { ...ctx, screen: "escalated", phase: "track", escalated: true };
    case "track_continue":
      return { ...ctx, screen: "complete", phase: "track" };
    case "complete":
      return { ...ctx, screen: "complete" };
    case "restart":
      return initialContext();
    case "dismiss_welcome":
      return { ...ctx, welcomeBack: false };
    case "continue":
      if (ctx.screen === "find_success" || ctx.screen === "find_not_covered") {
        return { ...ctx, screen: "access", phase: "access" };
      }
      return ctx;
    default:
      return ctx;
  }
}

export function getProvider(ctx: JourneyContext) {
  return ctx.providerId ? PROVIDERS[ctx.providerId] : undefined;
}

export function fullName(ctx: JourneyContext) {
  return `${ctx.firstName} ${ctx.lastName}`.trim() || "Jordan Rivera";
}

export function fboPayee(ctx: JourneyContext) {
  return `PensionBee FBO ${fullName(ctx)}`;
}

export function mailLine(ctx: JourneyContext) {
  const p = getProvider(ctx);
  if (p?.mailToUser) {
    return "Your home address on file — then forward in the prepaid envelope PensionBee sends you.";
  }
  return "PO Box 72, New York, NY 10272";
}

export { totalSteps };
