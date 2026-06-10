import type { JourneyResponse } from "./types";

export interface FooterActionSpec {
  label: string;
  action: Record<string, unknown>;
  key: string;
}

export interface FooterSpec {
  primary: FooterActionSpec | null;
  secondaries: FooterActionSpec[];
}

export function resolveFooterActions(
  data: JourneyResponse,
  showProviderPicker: boolean
): FooterSpec {
  const { screen, enrichment } = data;
  const state = screen.state;

  if (state === "complete") {
    return {
      primary: { label: "Start another rollover", action: { type: "restart" }, key: "shell_primary" },
      secondaries: [],
    };
  }

  if (state === "escalated") {
    return { primary: null, secondaries: [] };
  }

  if (state === "provider_unknown" || enrichment.requires_tax_selection || showProviderPicker) {
    return { primary: null, secondaries: [] };
  }

  if (screen.disambiguation_question && screen.disambiguation_options.length > 0) {
    return { primary: null, secondaries: [] };
  }

  if (state === "provider_identified" || state === "provider_not_covered") {
    const secondaries: FooterActionSpec[] = [];
    if (state === "provider_not_covered") {
      secondaries.push({
        label: "Talk to a BeeKeeper about this provider",
        action: { type: "handoff", reason: "provider_not_covered" },
        key: "shell_handoff",
      });
    }
    return { primary: null, secondaries };
  }

  if (
    state === "access_recovered" &&
    screen.secondary_actions.some((a) => /phone|form/i.test(a))
  ) {
    return { primary: null, secondaries: [] };
  }

  if (["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(state)) {
    return {
      primary: {
        label: screen.primary_action || "Done — next step",
        action: { type: "step", outcome: "done" },
        key: "shell_primary",
      },
      secondaries: [
        {
          label: "I'm stuck on this step",
          action: { type: "step", outcome: "stuck" },
          key: "shell_stuck",
        },
      ],
    };
  }

  if (state === "stuck") {
    return {
      primary: {
        label: screen.primary_action || "Talk to your BeeKeeper",
        action: { type: "escalate", reason: "stuck_on_step" },
        key: "shell_primary",
      },
      secondaries: [
        {
          label: "Try this step again",
          action: { type: "resume" },
          key: "shell_resume",
        },
      ],
    };
  }

  if (state === "initiated") {
    return {
      primary: {
        label: screen.primary_action || "Track my transfer",
        action: { type: "confirm_in_flight" },
        key: "shell_primary",
      },
      secondaries: screen.secondary_actions
        .filter((a) => /nothing arrived|help/i.test(a))
        .map((action, i) => ({
          label: action,
          action: { type: "escalate", reason: "tracking_delay" },
          key: `shell_track_sec_${i}`,
        })),
    };
  }

  if (state === "in_flight") {
    return {
      primary: {
        label: screen.primary_action || "Mark complete",
        action: { type: "mark_complete" },
        key: "shell_primary",
      },
      secondaries: screen.secondary_actions
        .filter((a) => /nothing arrived|help/i.test(a))
        .map((action, i) => ({
          label: action,
          action: { type: "escalate", reason: "tracking_delay" },
          key: `shell_track_sec_${i}`,
        })),
    };
  }

  if (state === "access_blocked") {
    return {
      primary: {
        label: screen.primary_action || "Continue",
        action: { type: "access_recovered" },
        key: "shell_primary",
      },
      secondaries: screen.secondary_actions
        .filter((a) => /locked|beekeeper/i.test(a))
        .map((action, i) => ({
          label: action,
          action: { type: "escalate", reason: "access_lockout" },
          key: `shell_access_sec_${i}`,
        })),
    };
  }

  return { primary: null, secondaries: [] };
}
