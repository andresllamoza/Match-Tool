/** Built-in demo API — active when no external API_URL is configured (zero-setup Vercel deploy). */
export function isDemoBackendEnabled(): boolean {
  if (process.env.FORCE_LIVE_API === "true") return false;
  if (process.env.DEMO_MODE === "false") return false;
  return !process.env.API_URL?.trim();
}
