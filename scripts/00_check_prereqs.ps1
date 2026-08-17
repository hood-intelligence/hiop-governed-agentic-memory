# Gate 0 — what is installed for last-mile submit
$ErrorActionPreference = "Continue"
Write-Host "=== HIOP CRDB x AWS RC1 prereqs ===" -ForegroundColor Cyan
$tools = @(
  @{n="python"; need=$true},
  @{n="git"; need=$true},
  @{n="docker"; need=$false},
  @{n="aws"; need=$false},
  @{n="sam"; need=$false},
  @{n="gh"; need=$false},
  @{n="ccloud"; need=$false}
)
foreach ($t in $tools) {
  $c = Get-Command $t.n -EA SilentlyContinue
  if ($c) {
    Write-Host ("[OK]  {0,-8} {1}" -f $t.n, $c.Source) -ForegroundColor Green
  } else {
    $tag = if ($t.need) { "NEED" } else { "opt " }
    $color = if ($t.need) { "Red" } else { "Yellow" }
    Write-Host ("[{0}] {1,-8} MISSING" -f $tag, $t.n) -ForegroundColor $color
  }
}
if (Get-Command docker -EA SilentlyContinue) {
  docker info 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK]  docker daemon running" -ForegroundColor Green
  } else {
    Write-Host "[opt ] docker present but daemon NOT running - start Docker Desktop" -ForegroundColor Yellow
  }
}
Write-Host ""
Write-Host "CRDB_DSN set?  $([bool]$env:CRDB_DSN)"
Write-Host "DEMO_URL set?  $([bool]$env:DEMO_URL)"
Write-Host ""
Write-Host "Next: create CockroachDB Cloud cluster, then scripts\01_apply_crdb_schema.py"
