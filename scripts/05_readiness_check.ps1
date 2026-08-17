# Scorecard: set CRDB_DSN and optionally DEMO_URL then run
$ErrorActionPreference = "Continue"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
Write-Host "=== READY TO SUBMIT scorecard ===" -ForegroundColor Cyan

$score = @{}

# Tests always
$env:HIOP_MEMORY_MODE = "fixture"
$env:PYTHONPATH = "src"
python -m pytest tests -q
$score["tests_7"] = ($LASTEXITCODE -eq 0)

# Live CRDB
if ($env:CRDB_DSN) {
  python scripts\01_apply_crdb_schema.py
  $a = ($LASTEXITCODE -eq 0)
  python scripts\02_run_live_demo.py
  $b = ($LASTEXITCODE -eq 0)
  $score["live_crdb"] = ($a -and $b)
} else {
  Write-Host "[ ] live_crdb — set CRDB_DSN" -ForegroundColor Yellow
  $score["live_crdb"] = $false
}

# Demo URL
if ($env:DEMO_URL) {
  try {
    $r = Invoke-RestMethod -Method POST -Uri $env:DEMO_URL -ContentType "application/json" -Body '{"goal":"lab safe"}' -TimeoutSec 60
    $score["demo_url"] = ($null -ne $r.results)
    Write-Host "demo_url OK backend=$($r.memory_backend)" -ForegroundColor Green
  } catch {
    Write-Host "demo_url FAIL: $_" -ForegroundColor Red
    $score["demo_url"] = $false
  }
} else {
  Write-Host "[ ] demo_url — set DEMO_URL after Lambda deploy" -ForegroundColor Yellow
  $score["demo_url"] = $false
}

# Git remote
$score["git_repo"] = (Test-Path "$Root\.git")
# GitHub public cannot be verified offline
Write-Host "[?] github_public — verify in browser" -ForegroundColor Yellow
Write-Host "[?] video — Founder records" -ForegroundColor Yellow

Write-Host ""
Write-Host "SCORE:"
$score.GetEnumerator() | ForEach-Object { Write-Host ("  {0}={1}" -f $_.Key, $_.Value) }
$ready = $score["tests_7"] -and $score["live_crdb"] -and $score["demo_url"]
if ($ready) {
  Write-Host "PROGRAMMATIC GATES 1-2 PASS — still need public GitHub + video for READY TO SUBMIT" -ForegroundColor Green
} else {
  Write-Host "Still CONDITIONALLY READY — complete missing gates" -ForegroundColor Yellow
}
