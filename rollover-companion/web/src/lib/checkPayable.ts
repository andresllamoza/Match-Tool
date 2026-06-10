export const SYNTHETIC_CUSTOMER_NAME = "Jordan Rivera";
export const PAYABLE_NAME_TOKEN = "[your name]";

export function formatCheckPayable(
  template: string,
  firstName: string = "Jordan",
  lastName: string = "Rivera"
): string {
  if (!template) return template;
  return template.replace(PAYABLE_NAME_TOKEN, `${firstName} ${lastName}`.trim());
}

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
