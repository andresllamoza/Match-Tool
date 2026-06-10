import type { JourneyScreen } from "./types";

export function deriveSourceStatus(
  screen: JourneyScreen
): "verified" | "reconstructed" | null {
  if (screen.has_reconstructed_content) return "reconstructed";
  if (screen.guidance.some((g) => g.reconstructed)) return "reconstructed";
  if (screen.provider && ["provider_identified", "provider_not_covered"].includes(screen.state)) {
    return "verified";
  }
  if (
    ["online_in_progress", "phone_in_progress", "forms_in_progress"].includes(screen.state) &&
    screen.provider
  ) {
    return "verified";
  }
  return null;
}
