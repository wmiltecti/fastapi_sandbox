# Disable Supabase IPv4 add-on via Management API (PowerShell)
# Requires environment variables: $env:SUPABASE_ACCESS_TOKEN and $env:PROJECT_REF
# Usage: $env:SUPABASE_ACCESS_TOKEN='token'; $env:PROJECT_REF='projref'; .\scripts\disable_ipv4.ps1

if (-not $env:SUPABASE_ACCESS_TOKEN -or -not $env:PROJECT_REF) {
    Write-Error "SUPABASE_ACCESS_TOKEN and PROJECT_REF environment variables must be set"
    exit 2
}

$apiBase = "https://api.supabase.com/v1/projects/$($env:PROJECT_REF)"

Write-Host "Disabling IPv4 add-on..."
Invoke-RestMethod -Uri "$apiBase/billing/addons/ipv4" -Method Delete -Headers @{ Authorization = "Bearer $($env:SUPABASE_ACCESS_TOKEN)" } | ConvertTo-Json -Depth 4
Write-Host "Done. Verify in the Supabase dashboard." 
