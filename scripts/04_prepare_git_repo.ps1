# Init git repo for public GitHub publish (no push — Founder adds remote)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

$gitignore = @"
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
dist/
data/*.jsonl
data/last_*.json
.env
.env.*
*.pem
.aws-sam/
"@
Set-Content -Path (Join-Path $Root ".gitignore") -Value $gitignore -Encoding utf8

if (-not (Test-Path (Join-Path $Root ".git"))) {
  git init -b main
  git add -A
  git status
  git commit -m "HIOP Governed Agentic Memory RC1 — CockroachDB x AWS contest entry"
  Write-Host ""
  Write-Host "OK: local main commit ready."
} else {
  Write-Host "OK: .git already exists — review git status"
  git status -sb
}

Write-Host ""
Write-Host "Browser: create PUBLIC empty repo e.g. hiop-governed-agentic-memory"
Write-Host "Then:"
Write-Host '  git remote add origin https://github.com/YOUR_ORG/hiop-governed-agentic-memory.git'
Write-Host "  git push -u origin main"
Write-Host "Confirm LICENSE (Apache-2.0) shows on GitHub About / root."
