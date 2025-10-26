# Enable Supabase IPv4 add-on via Management API (PowerShell)
# Requires environment variables: $env:SUPABASE_ACCESS_TOKEN and $env:PROJECT_REF
# Usage: $env:SUPABASE_ACCESS_TOKEN='token'; $env:PROJECT_REF='projref'; .\scripts\enable_ipv4.ps1

if (-not $env:SUPABASE_ACCESS_TOKEN -or -not $env:PROJECT_REF) {
    Write-Error "SUPABASE_ACCESS_TOKEN and PROJECT_REF environment variables must be set"
    exit 2
}

$apiBase = "https://api.supabase.com/v1/projects/$($env:PROJECT_REF)"

Write-Host "Getting current add-ons status..."
Invoke-RestMethod -Uri "$apiBase/billing/addons" -Method Get -Headers @{ Authorization = "Bearer $($env:SUPABASE_ACCESS_TOKEN)" } | ConvertTo-Json -Depth 4

$yn = Read-Host "Enable IPv4 add-on for project $($env:PROJECT_REF)? (y/N)"
if ($yn -match '^[Yy]') {
    Write-Host "Enabling IPv4 add-on..."
    $body = @{ addon_type = 'ipv4' } | ConvertTo-Json
    Invoke-RestMethod -Uri "$apiBase/addons" -Method Post -Headers @{ Authorization = "Bearer $($env:SUPABASE_ACCESS_TOKEN)"; 'Content-Type' = 'application/json' } -Body $body | ConvertTo-Json -Depth 4
    Write-Host "Done. Check the project billing/addons in supabase dashboard." 
} else {
    Write-Host "Aborted."
}
