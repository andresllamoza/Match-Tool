import type { DecisionMode } from "./decisionMode";

export function stepHelperCopy(decision: DecisionMode): string | null {
  switch (decision) {
    case "employer":
      return "We only use your employer name to match you to the correct 401(k) recordkeeper — never to sell your data.";
    case "tax":
      return "Your tax type tells us which IRA bucket receives the rollover. Most 401(k)s are pre-tax.";
    case "access":
      return "Logging in lets you complete the rollover online in minutes. If you're locked out, we'll help you recover access.";
    case "channel":
      return "Pick one path to start — you can switch to phone or paper later if needed.";
    case "channel_step":
      return "Complete this step in your provider portal or on the phone, then tap done when finished.";
    case "disambiguation":
      return "One quick detail helps us route you to the right plan administrator.";
    case "provider_pick":
      return "Selecting your provider skips the employer lookup and goes straight to rollover steps.";
    case "track":
      return "We'll help you track your check or transfer until it lands in your PensionBee IRA.";
    case "stuck":
      return "A BeeKeeper can walk through this step with you — no judgment, just clarity.";
    default:
      return null;
  }
}
