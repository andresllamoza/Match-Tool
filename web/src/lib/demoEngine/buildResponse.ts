import type { JourneyResponse, JourneyScreen } from "@/lib/types";
import {
  DESTINATION,
  MAILING,
  PAYEE_TEMPLATE,
  PHONE_BY_PROVIDER,
  resolveProvider,
} from "./constants";
import type { DemoState } from "./state";

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
  const provider = state.provider || "your provider";
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
    case "provider_identified":
      return {
        ...base,
        confidence_tier: "high",
        headline: "Can you log in to your 401(k)?",
        body: `We matched your plan to ${provider}. Logging in is the fastest path to start your rollover.`,
        primary_action: "Yes, I can log in",
        secondary_actions: ["No, I'm locked out"],
      };
    case "access_recovered":
      return {
        ...base,
        headline: "How would you like to roll over?",
        body: "Pick one path to start. You can switch later if needed.",
        primary_action: "Choose a channel",
        secondary_actions: [],
      };
    case "online_in_progress":
      return {
        ...base,
        headline: `Roll over online with ${provider}`,
        body: "Complete each step in your provider portal, then tap done.",
        primary_action: state.stepIndex >= state.totalSteps - 1 ? "I've completed this rollover" : "Done with this step",
        secondary_actions: [],
        has_reconstructed_content: false,
      };
    case "phone_in_progress":
      return {
        ...base,
        headline: `Roll over by phone with ${provider}`,
        body: "Call your provider and use the script below. Tap done when finished.",
        primary_action: state.stepIndex >= state.totalSteps - 1 ? "I've completed this rollover" : "Done with this step",
        secondary_actions: [],
      };
    case "initiated":
      return {
        ...base,
        headline: "Your rollover is in motion",
        body: "We'll help you track your transfer until it lands in your PensionBee IRA.",
        primary_action: "Confirm transfer started",
        secondary_actions: ["Nothing arrived yet — get help"],
      };
    case "in_flight":
      return {
        ...base,
        headline: "Tracking your rollover",
        body: "Your transfer is in progress. Typical timeline is 2–4 weeks.",
        primary_action: "Mark complete",
        secondary_actions: ["Nothing arrived yet — get help"],
      };
    case "complete":
      return {
        ...base,
        headline: "You're all set!",
        body: "You earned your 1% match — welcome to PensionBee.",
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
  const provider = state.provider || resolveProvider(state.employer || "");
  const phone = PHONE_BY_PROVIDER[provider] || "800-555-0100";

  const channelSteps = [
    {
      say: `I'd like to roll over my 401(k) from ${state.employer || "my former employer"} to PensionBee.`,
      label: "Step 1",
    },
    {
      say: "This is a direct rollover to another retirement account — not a withdrawal to me personally.",
      label: "Step 2",
    },
    {
      say: `Please make the check payable to: ${PAYEE_TEMPLATE}, mailed to ${MAILING}.`,
      label: "Step 3",
    },
  ];

  const step = channelSteps[Math.min(state.stepIndex, channelSteps.length - 1)];

  const enrichment: JourneyResponse["enrichment"] = {
    mailing_address: MAILING,
    destination_name: DESTINATION,
    forward_step_required: false,
    general_path: false,
    requires_tax_selection: state.state === "provider_identified" && !state.taxType,
    tax_options: state.state === "provider_identified" && !state.taxType
      ? [
          { id: "pre_tax", label: "Pre-tax (Traditional IRA)", hint: "Most common 401(k) balance" },
          { id: "roth", label: "Roth (Roth IRA)", hint: "After-tax contributions and earnings" },
          { id: "both", label: "Both pre-tax and Roth", hint: "Split across two IRA types" },
        ]
      : [],
    check_destination: "PensionBee IRA",
    lookup:
      state.employer && state.provider
        ? { employer_query: state.employer, matched_provider: state.provider }
        : null,
    channel_context:
      state.channel &&
      ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(state.state)
        ? {
            channel: state.channel,
            say_this: state.channel === "phone" ? step.say : channelSteps[state.stepIndex]?.say || step.say,
            phone: state.channel === "phone" ? phone : null,
            intro: state.channel === "phone" ? "When the representative answers, say:" : null,
            check_payable: PAYEE_TEMPLATE,
            mailing_address: MAILING,
            rep_questions: [
              {
                question: "Is this a direct rollover?",
                answer: "Yes — direct rollover to PensionBee, not a distribution to me.",
              },
            ],
            step_label: step.label,
            portal_menu_hints: state.channel === "online" ? ["Withdrawals", "Rollovers", "Distributions"] : [],
            destination_hints: [],
          }
        : null,
    track:
      ["initiated", "in_flight"].includes(state.state)
        ? {
            typical_timeline: "2 to 4 weeks",
            check_destination: DESTINATION,
            follow_up_days: 28,
            nothing_arrived_message:
              "If nothing has arrived by day 28, a BeeKeeper can trace your rollover with the provider.",
            mechanism_note: "Electronic transfer to your PensionBee IRA",
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
      lookup_confidence_tier: state.state === "provider_identified" ? "high" : null,
      uncovered_provider: null,
      history_stack: state.history,
    },
    screen,
    step_index: state.stepIndex,
    total_steps: state.totalSteps,
    enrichment,
    provider_intel: {},
  };
}
