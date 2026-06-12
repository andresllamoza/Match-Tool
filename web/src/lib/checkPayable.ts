export function isFboPayableLine(text: string): boolean {
  const lower = text.toLowerCase();
  return lower.includes("fbo") && lower.includes("pensionbee");
}

export function usesCheckMailing(mechanism?: string | null, checkDestination?: string | null): boolean {
  if (mechanism === "two_hop_acat") return false;
  const dest = (checkDestination || "").toLowerCase();
  if (dest.includes("no check") || dest.includes("acat")) return false;
  return true;
}

export function showMailingDetails(
  sayThis: string,
  stepIndex: number,
  totalSteps: number,
  options?: { mechanism?: string | null; checkDestination?: string | null }
): boolean {
  if (!usesCheckMailing(options?.mechanism, options?.checkDestination)) {
    return false;
  }
  const lower = sayThis.toLowerCase();
  if (["check", "payable", "mail", "mailing address"].some((w) => lower.includes(w))) {
    return true;
  }
  if (totalSteps <= 0) return false;
  return stepIndex >= totalSteps - 2;
}
