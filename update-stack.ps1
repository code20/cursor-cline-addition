# update-stack.ps1 — quick health check for your AI coding stack
$ErrorActionPreference = "Stop"
Set-Location $env:USERPROFILE\.config\ultra-lite-proxy

Write-Host "=== 1/4  Python dependencies (proxy) ==="
. .\venv\Scripts\Activate.ps1
pip list --outdated
deactivate

Write-Host "
=== 2/4  Global MCP server packages ==="
npm outdated -g

Write-Host "
=== 3/4  OpenRouter model availability ==="
if (Test-Path .\check_models.ps1) {
    .\check_models.ps1
} else {
    Write-Host "check_models.ps1 not found — save the watcher snippet as a separate file."
}

Write-Host "
=== 4/4  Cursor & Cline ==="
Write-Host "Cursor changelog: https://cursor.sh/changelog"
Write-Host "Cline releases:    https://github.com/cline/cline/releases"
