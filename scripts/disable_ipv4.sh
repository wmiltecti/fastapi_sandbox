#!/usr/bin/env bash
set -euo pipefail

: "\nDisable Supabase IPv4 add-on via Management API.\nRequires SUPABASE_ACCESS_TOKEN and PROJECT_REF environment variables.\nUsage:\n  SUPABASE_ACCESS_TOKEN=... PROJECT_REF=... ./scripts/disable_ipv4.sh\n"

if [ -z "${SUPABASE_ACCESS_TOKEN:-}" ] || [ -z "${PROJECT_REF:-}" ]; then
  echo "ERROR: SUPABASE_ACCESS_TOKEN and PROJECT_REF must be set in environment"
  exit 2
fi

API_BASE="https://api.supabase.com/v1/projects/$PROJECT_REF"

echo "Disabling IPv4 add-on..."
curl -s -X DELETE "$API_BASE/billing/addons/ipv4" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Accept: application/json" | jq .

echo "Done. Verify in the Supabase dashboard." 
