export type DecisionMode =
  | "tax"
  | "employer"
  | "provider_pick"
  | "disambiguation"
  | "access"
  | "channel"
  | "channel_step"
  | "track"
  | "stuck"
  | "confirm"
  | "done";

export function decisionTitle(decision: DecisionMode, screenQuestion?: string | null): string {
  switch (decision) {
    case "tax":
      return "How is your old 401(k) taxed?";
    case "provider_pick":
      return "Select your 401(k) provider";
    case "disambiguation":
      return screenQuestion || "Narrow it down";
    case "access":
      return "Can you log in to your old 401(k) account right now?";
    case "channel":
      return "How would you like to start your rollover?";
    case "channel_step":
      return "Ready for the next step?";
    case "stuck":
      return "Let's get you unstuck";
    case "track":
      return "Track your rollover";
    default:
      return "Continue your rollover";
  }
}
