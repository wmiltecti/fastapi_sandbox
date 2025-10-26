#!/usr/bin/env bash
set -euo pipefail

: "\nEnable Supabase IPv4 add-on via Management API.\nRequires SUPABASE_ACCESS_TOKEN and PROJECT_REF environment variables.\nUsage:\n  SUPABASE_ACCESS_TOKEN=... PROJECT_REF=... ./scripts/enable_ipv4.sh\n"

if [ -z "${SUPABASE_ACCESS_TOKEN:-}" ] || [ -z "${PROJECT_REF:-}" ]; then
  echo "ERROR: SUPABASE_ACCESS_TOKEN and PROJECT_REF must be set in environment"
  exit 2
fi

API_BASE="https://api.supabase.com/v1/projects/$PROJECT_REF"

echo "Getting current add-ons status..."
curl -s -X GET "$API_BASE/billing/addons" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Accept: application/json" | jq .

read -p "Enable IPv4 add-on for project $PROJECT_REF? [y/N] " yn
case "$yn" in
  [Yy]*)
    echo "Enabling IPv4 add-on..."
    curl -s -X POST "$API_BASE/addons" \
      -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"addon_type":"ipv4"}' | jq .
    echo "Done. Check the project billing/addons in supabase dashboard." ;;
  *)
    echo "Aborted." ;;
esac
