export function employerSearchError(message: string | null, empty: boolean): string | null {
  if (!message && !empty) return null;
  if (empty) {
    return "Tell us your former employer so we can locate the right 401(k) provider.";
  }
  const lower = (message || "").toLowerCase();
  if (
    lower.includes("timeout") ||
    lower.includes("timed out") ||
    lower.includes("network") ||
    lower.includes("fetch") ||
    lower.includes("connect") ||
    lower.includes("unreachable") ||
    lower.includes("503") ||
    lower.includes("502")
  ) {
    return "We're having trouble reaching our servers. Check your connection and try again — your BeeKeeper can help if this keeps happening.";
  }
  if (lower.includes("not found") || lower.includes("no match") || lower.includes("unknown employer")) {
    return "We couldn't find a plan for that employer. Try the parent company name (e.g. \"Alphabet\" instead of \"Google\"), or tap \"I already know my provider\" below.";
  }
  if (lower.includes("employer") || lower.includes("invalid") || lower.includes("required")) {
    return "We couldn't quite find that employer. Try searching for the parent company name, or tap \"I already know my provider\" below.";
  }
  return "We couldn't quite find that employer. Try searching for the parent company name, or tap \"I already know my provider\" below.";
}
