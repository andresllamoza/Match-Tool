import type { JourneyResponse, JourneyScreen } from "@/lib/types";
import { DESTINATION, MAILING, PAYEE_TEMPLATE, PHONE_BY_PROVIDER } from "./constants";
import { channelStepContent, providerGuideInfo } from "./playbook";
import type { DemoState } from "./state";

function recordkeeper(state: DemoState): string | null {
  return state.provider || state.uncoveredProvider;
}

function isGeneralPath(state: DemoState): boolean {
  return Boolean(state.uncoveredProvider);
}

function phaseFor(state: DemoState): JourneyResponse["screen"]["phase"] {
  if (state.state === "provider_unknown") return "find";
  if (["provider_identified", "provider_not_covered", "access_blocked", "access_recovered"].includes(state.state)) {
    return "access";
  }
  if (["online_in_progress", "phone_in_progress", "forms_in_progress", "stuck"].includes(state.state)) {
    return "rollover";
  }
  return "track";
}

function screenFor(state: DemoState): JourneyScreen {
  const rk = recordkeeper(state);
  const guide = providerGuideInfo(rk);
  const id = state.journeyId;

  const base: JourneyScreen = {
    journey_id: id,
    state: state.state,
    phase: phaseFor(state),
    provider: state.provider,
    channel: state.channel,
    headline: "",
    body: "",
    primary_action: "Continue",
    secondary_actions: [],
    guidance: [],
    edge_cases: [],
    active_escalations: [],
    disambiguation_question: null,
    disambiguation_options: [],
    confidence_tier: null,
    provenance_warning: null,
    has_reconstructed_content: false,
    agent_notes: [],
    next_beekeeper_script: null,
    sla_note: null,
  };

  switch (state.state) {
    case "provider_unknown":
      return {
        ...base,
        headline: "Find your old 401(k)",
        body: "Roll your old 401(k) to PensionBee and get a 1% match on eligible transfers.",
        primary_action: "Search for my employer",
        secondary_actions: ["I already know my 401(k) provider"],
      };
    case "provider_identified": {
      const portal = guide.portal || guide.accessPortalName || rk;
      return {
        ...base,
        confidence_tier: "high",
        headline: `Can you log in to ${portal}?`,
        body: guide.providerIdentifiedMessage || `We matched your plan to ${rk}.`,
        primary_action: "Yes, I can log in",
        secondary_actions: ["No, I'm locked out"],
      };
    }
    case "provider_not_covered": {
      const name = state.uncoveredProvider || "your recordkeeper";
      const portal = guide.portal || guide.accessPortalName || `${name}'s retirement portal`;
      return {
        ...base,
        confidence_tier: "high",
        headline: `Can you log in to ${portal}?`,
        body: `Your 401(k) appears to be with ${name}. ${guide.providerIdentifiedMessage || ""}`.trim(),
        primary_action: "Yes, I can log in",
        secondary_actions: ["No, I'm locked out", "Talk to a BeeKeeper"],
        provenance_warning:
          "Using general rollover steps — provider-specific path not yet in library.",
      };
    }
    case "access_blocked": {
      const portal = guide.accessPortalName || guide.portal || rk;
      const resetSteps = guide.accessResetSteps.length
        ? guide.accessResetSteps
        : [`Use ${portal}'s password reset, then come back when you can log in.`];
      return {
        ...base,
        headline: `Let's get you into ${portal}`,
        body: "Use the recovery steps below, then return when you can log in.",
        primary_action: "I'm in now",
        secondary_actions: ["Still locked out — get a BeeKeeper"],
        guidance: [
          ...resetSteps.map((text) => ({
            text,
            owner: "customer" as const,
            source_status: "verified" as const,
            reconstructed: false,
          })),
          ...(guide.lockoutPhone
            ? [
                {
                  text: `Locked out? Call ${guide.lockoutPhone} and say: ${guide.lockoutScript || "I need help accessing my account to request a rollover."}`,
                  owner: "customer" as const,
                  source_status: "verified" as const,
                  reconstructed: false,
                },
              ]
            : []),
        ],
      };
    }
    case "access_recovered":
      if (!state.taxType) {
        return {
          ...base,
          phase: "rollover",
          headline: "What type of funds are you rolling over?",
          body: "Most 401(k) balances are pre-tax. Roth accounts are after-tax.",
          primary_action: "Pre-tax (Traditional IRA)",
          secondary_actions: ["Roth (Roth IRA)", "Both pre-tax and Roth"],
        };
      }
      return {
        ...base,
        phase: "rollover",
        headline: `How would you like to roll over with ${rk}?`,
        body: guide.preferredPath || DESTINATION,
        primary_action: "Online portal",
        secondary_actions: ["Phone"],
      };
    case "online_in_progress": {
      const onlineStep = channelStepContent(rk, "online", state.stepIndex);
      return {
        ...base,
        provider: rk,
        headline: `Step ${state.stepIndex + 1} of ${state.totalSteps}`,
        body: onlineStep.sayThis,
        primary_action:
          state.stepIndex >= state.totalSteps - 1 ? "I've completed this rollover" : "Done with this step",
        secondary_actions: [],
        has_reconstructed_content: onlineStep.hasReconstructed,
        provenance_warning: onlineStep.hasReconstructed
          ? "Some portal step wording is reconstructed — spot-check against the live Scribe."
          : isGeneralPath(state)
            ? "Using general rollover steps — menu names may vary in your portal."
            : null,
      };
    }
    case "phone_in_progress": {
      const phoneStep = channelStepContent(rk, "phone", state.stepIndex);
      const body =
        state.stepIndex === 0 && phoneStep.phoneIntro
          ? `${phoneStep.phoneIntro}\n\n${phoneStep.sayThis}`
          : phoneStep.sayThis;
      return {
        ...base,
        provider: rk,
        headline: `Step ${state.stepIndex + 1} of ${state.totalSteps}`,
        body,
        primary_action:
          state.stepIndex >= state.totalSteps - 1 ? "I've completed this rollover" : "Done with this step",
        secondary_actions: [],
        provenance_warning: isGeneralPath(state)
          ? "Using general phone script — your provider's IVR may differ."
          : null,
      };
    }
    case "forms_in_progress": {
      const formStep = channelStepContent(rk, "forms", state.stepIndex);
      return {
        ...base,
        provider: rk,
        headline: formStep.stepLabel,
        body: formStep.sayThis,
        primary_action:
          state.stepIndex >= state.totalSteps - 1 ? "I've completed this rollover" : "Done with this step",
        secondary_actions: [],
      };
    }
    case "initiated":
      return {
        ...base,
        provider: rk,
        headline: "Your rollover is in motion",
        body:
          guide.rolloverInitiatedMessage ||
          "We'll help you track your transfer until it lands in your PensionBee IRA.",
        primary_action: "Confirm transfer started",
        secondary_actions: ["Nothing arrived yet — get help"],
      };
    case "in_flight":
      return {
        ...base,
        provider: rk,
        headline: "Tracking your rollover",
        body:
          guide.inFlightMessage ||
          "Your transfer is in progress. Typical timeline is 2–4 weeks.",
        primary_action: "Mark complete",
        secondary_actions: ["Nothing arrived yet — get help"],
      };
    case "complete":
      return {
        ...base,
        provider: rk,
        headline: "You're all set!",
        body: guide.completeMessage || "You earned your 1% match — welcome to PensionBee.",
        primary_action: "Done",
        secondary_actions: [],
      };
    case "escalated":
      return {
        ...base,
        headline: "A BeeKeeper will take it from here",
        body: "Sam has your context and will follow up shortly.",
        primary_action: "Close",
        secondary_actions: [],
      };
    default:
      return base;
  }
}

export function buildDemoResponse(state: DemoState): JourneyResponse {
  const screen = screenFor(state);
  const rk = recordkeeper(state);
  const generalPath = isGeneralPath(state);
  const guide = providerGuideInfo(rk);
  const phone = guide.phone || (rk ? PHONE_BY_PROVIDER[rk] : null) || "800-555-0100";

  const inChannel =
    state.channel &&
    ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(state.state);
  const stepContent =
    inChannel && state.channel ? channelStepContent(rk, state.channel, state.stepIndex) : null;

  const enrichment: JourneyResponse["enrichment"] = {
    mailing_address: MAILING,
    destination_name: DESTINATION,
    forward_step_required: stepContent?.forwardStepRequired ?? guide.forwardStepRequired,
    general_path: generalPath,
    preferred_path: guide.preferredPath,
    provider_portal: guide.portal,
    provider_phone: guide.phone,
    requires_tax_selection: state.state === "access_recovered" && !state.taxType,
    tax_options:
      state.state === "access_recovered" && !state.taxType
        ? [
            { id: "pre_tax", label: "Pre-tax (Traditional IRA)", hint: "Most common 401(k) balance" },
            { id: "roth", label: "Roth (Roth IRA)", hint: "After-tax contributions and earnings" },
            { id: "both", label: "Both pre-tax and Roth", hint: "Split across two IRA types" },
          ]
        : [],
    mechanism: stepContent?.mechanism ?? guide.mechanism,
    check_destination: stepContent?.checkDestination ?? guide.checkDestination ?? "PensionBee IRA",
    lookup:
      state.employer && rk
        ? { employer_query: state.employer, matched_provider: rk }
        : null,
    channel_context: stepContent
      ? {
          channel: state.channel!,
          say_this: stepContent.sayThis,
          phone: state.channel === "phone" ? phone : null,
          intro: stepContent.phoneIntro,
          check_payable: PAYEE_TEMPLATE,
          mailing_address: MAILING,
          rep_questions: stepContent.repQuestions,
          step_label: stepContent.stepLabel,
          portal_name: stepContent.portalName,
          portal_menu_hints: stepContent.portalMenuHints,
          destination_hints: stepContent.destinationHints,
        }
      : null,
    track: ["initiated", "in_flight"].includes(state.state)
      ? {
          typical_timeline: "2 to 4 weeks",
          check_destination: guide.checkDestination || DESTINATION,
          follow_up_days: 28,
          nothing_arrived_message:
            "If nothing has arrived by day 28, a BeeKeeper can trace your rollover with the provider.",
          mechanism_note: generalPath
            ? "Direct rollover to your PensionBee IRA"
            : "Electronic transfer to your PensionBee IRA",
        }
      : null,
  };

  return {
    context: {
      journey_id: state.journeyId,
      state: state.state,
      provider: state.provider,
      channel: state.channel,
      step_index: state.stepIndex,
      flags: {},
      employer_query: state.employer,
      disambiguation_question: null,
      disambiguation_options: [],
      tax_fund_type: state.taxType,
      lookup_confidence_tier:
        state.state === "provider_identified" || state.state === "provider_not_covered" ? "high" : null,
      uncovered_provider: state.uncoveredProvider,
      history_stack: state.history,
    },
    screen,
    step_index: state.stepIndex,
    total_steps: state.totalSteps,
    enrichment,
    provider_intel: {},
  };
}
