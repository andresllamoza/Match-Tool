export function isFboPayableLine(text: string): boolean {
  const lower = text.toLowerCase();
  return lower.includes("fbo") && lower.includes("pensionbee");
}

export function showMailingDetails(
  sayThis: string,
  stepIndex: number,
  totalSteps: number
): boolean {
  const lower = sayThis.toLowerCase();
  if (
    ["check", "payable", "mail", "pensionbee", "destination", "ira"].some((w) =>
      lower.includes(w)
    )
  ) {
    return true;
  }
  if (totalSteps <= 0) return false;
  return stepIndex >= totalSteps - 3;
}
