# Deploy to Vercel (CEO / VC preview — zero setup)

1. Import this repo on [vercel.com](https://vercel.com)
2. Set **Root Directory** to `web`
3. Deploy — **no environment variables required**

The app ships with a **built-in demo API** so `/` and `/app` are fully interactive immediately: employer search, match, channel walkthrough, tracking, and completion.

You will see a slim banner: *Interactive preview with guided demo data*.

## Production (real employer lookups)

After Railway is connected to the repo and deployed:

1. Copy your Railway public URL (Networking → domain)
2. Vercel → **Settings** → **Environment Variables** → add:

| Name | Value |
|------|--------|
| `API_URL` | `https://your-service.up.railway.app` (no trailing slash) |

3. **Redeploy** Vercel (Deployments → ⋯ → Redeploy)

The demo banner disappears; `/app` uses the live employer index.

```bash
VERCEL_URL=https://your-app.vercel.app bash scripts/verify-production.sh
```

See `rollover-companion/DEPLOY_API.md` for Railway details.
