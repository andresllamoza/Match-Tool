export function employerSearchError(message: string | null, empty: boolean): string | null {
  if (!message && !empty) return null;
  if (empty) {
    return "Tell us your former employer so we can locate the right 401(k) provider.";
  }
  const lower = (message || "").toLowerCase();
  if (lower.includes("not found") || lower.includes("404") || lower.includes("connect")) {
    return "We're having trouble reaching the rollover engine. Check your connection and try again — your BeeKeeper can help if this keeps happening.";
  }
  if (lower.includes("employer") || lower.includes("invalid") || lower.includes("required")) {
    return "We couldn't quite find that provider. Try searching for the parent company name, or tap \"I already know my provider\" below.";
  }
  return "We couldn't quite find that provider. Try searching for the parent company name, or tap \"I already know my provider\" below.";
}
