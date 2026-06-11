export function bootstrapConnectionError(message: string | null): string {
  const lower = (message || "").toLowerCase();

  if (lower.includes("api_url is not set") || lower.includes("api_unreachable")) {
    return "The rollover engine isn't connected yet. Deploy the API on Railway (root: rollover-companion), then set API_URL on Vercel and redeploy.";
  }
  if (lower.includes("cors") || lower.includes("railway")) {
    return message || "Could not reach the rollover API. Confirm Railway is running and CORS_ORIGINS includes this site.";
  }
  if (
    lower.includes("timeout") ||
    lower.includes("timed out") ||
    lower.includes("network") ||
    lower.includes("fetch failed") ||
    lower.includes("connect") ||
    lower.includes("unreachable") ||
    lower.includes("503") ||
    lower.includes("502")
  ) {
    return "We're having trouble reaching our servers. Check your connection and try again — your BeeKeeper can help if this keeps happening.";
  }
  return (
    message ||
    "We couldn't load your rollover session. Refresh the page or try again — a BeeKeeper can help if this persists."
  );
}

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
    lower.includes("fetch failed") ||
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
