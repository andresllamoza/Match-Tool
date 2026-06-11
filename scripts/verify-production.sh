#!/usr/bin/env bash
# Smoke-check Railway API + optional Vercel web after deploy.
# Usage:
#   RAILWAY_URL=https://your-api.up.railway.app bash scripts/verify-production.sh
#   VERCEL_URL=https://your-app.vercel.app bash scripts/verify-production.sh
set -euo pipefail

RAILWAY_URL="${RAILWAY_URL:-}"
VERCEL_URL="${VERCEL_URL:-}"

if [[ -z "$RAILWAY_URL" && -z "$VERCEL_URL" ]]; then
  echo "Set RAILWAY_URL and/or VERCEL_URL"
  exit 1
fi

check_api() {
  local base="${1%/}"
  echo "==> API health: $base/api/health"
  curl -fsS "$base/api/health" | grep -q '"status":"ok"' || {
    echo "FAIL: health check"
    exit 1
  }
  echo "OK"

  echo "==> Journey start: $base/api/journey/start"
  local jid
  jid=$(curl -fsS -X POST "$base/api/journey/start" -H 'Content-Type: application/json' -d '{}' \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['context']['journey_id'])")
  [[ -n "$jid" ]] || { echo "FAIL: no journey_id"; exit 1; }
  echo "OK journey_id=$jid"

  echo "==> Lookup Target"
  curl -fsS -X POST "$base/api/journey/$jid/action" \
    -H 'Content-Type: application/json' \
    -d '{"type":"lookup","employer":"Target"}' \
    | grep -q 'provider_identified' || {
    echo "FAIL: lookup"
    exit 1
  }
  echo "OK"
}

check_vercel() {
  local base="${1%/}"
  echo "==> Vercel health proxy: $base/api/health"
  curl -fsS "$base/api/health" | grep -q '"status":"ok"' || {
    echo "FAIL: Vercel /api/health"
    exit 1
  }
  echo "OK"

  echo "==> Vercel journey (live or demo)"
  local body
  body=$(curl -fsS -X POST "$base/api/journey/start" -H 'Content-Type: application/json' -d '{}')
  if echo "$body" | grep -q 'demo_v1_'; then
    echo "WARN: demo mode — set API_URL on Vercel to your Railway URL and redeploy"
  elif echo "$body" | grep -q 'provider_unknown'; then
    echo "OK live API via Vercel proxy"
  else
    echo "FAIL: unexpected journey response"
    echo "$body" | head -c 300
    exit 1
  fi
}

[[ -n "$RAILWAY_URL" ]] && check_api "$RAILWAY_URL"
[[ -n "$VERCEL_URL" ]] && check_vercel "$VERCEL_URL"

echo ""
echo "All checks passed."
