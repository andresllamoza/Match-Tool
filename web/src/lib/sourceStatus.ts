import type { JourneyContext, JourneyScreen } from "./types";

export function deriveSourceStatus(
  screen: JourneyScreen,
  context?: Pick<JourneyContext, "uncovered_provider">
): "verified" | "reconstructed" | null {
  if (screen.has_reconstructed_content) return "reconstructed";
  if (screen.guidance.some((g) => g.reconstructed)) return "reconstructed";
  const recordkeeper = screen.provider || context?.uncovered_provider;
  if (recordkeeper && ["provider_identified", "provider_not_covered"].includes(screen.state)) {
    return "verified";
  }
  if (
    ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(screen.state) &&
    recordkeeper
  ) {
    return "verified";
  }
  return null;
}
