# Deploy to Vercel (CEO / VC preview — zero setup)

1. Import this repo on [vercel.com](https://vercel.com)
2. Set **Root Directory** to `web`
3. Deploy — **no environment variables required**

The app ships with a **built-in demo API** so `/` and `/app` are fully interactive immediately: employer search, match, channel walkthrough, tracking, and completion.

You will see a slim banner: *Interactive preview with guided demo data*.

## Production (real employer lookups)

When ready, deploy `rollover-companion/` on Railway and add:

| Vercel env | Value |
|------------|--------|
| `API_URL` | Your Railway URL (no trailing slash) |

Redeploy Vercel. The banner disappears and lookups use the live 89k employer index.

See `rollover-companion/DEPLOY_API.md` for Railway steps.
