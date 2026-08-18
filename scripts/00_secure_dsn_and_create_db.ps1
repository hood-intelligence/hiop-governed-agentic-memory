# Local-only: paste DSN in this window. Never echo it. Never send it to Grok.
$ErrorActionPreference = "Stop"
Write-Host "Paste the Cockroach General connection string (Windows)."
Write-Host "It will not be printed back. Target database will be hiop_agent_memory, NOT hiop_dev."
$dsn = Read-Host "CRDB_DSN"
if (-not $dsn) { throw "empty DSN" }

# Rewrite /hiop_dev or any db to /defaultdb for CREATE DATABASE
function Set-DbPath([string]$url, [string]$db) {
  return [regex]::Replace($url, '/[A-Za-z0-9_]+(\?|$)', "/$db`$1")
}

$defaultUrl = Set-DbPath $dsn "defaultdb"
$memUrl = Set-DbPath $dsn "hiop_agent_memory"

$py = @"
import os, sys
import psycopg
url = os.environ['TMP_CRDB_DEFAULT']
# refuse if someone passed hiop_dev as the connect db for writes after rewrite we use defaultdb
if '/hiop_dev' in url.split('?')[0]:
    print('REFUSE: still targeting hiop_dev')
    sys.exit(3)
with psycopg.connect(url) as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute('SELECT current_database()')
        db = cur.fetchone()[0]
        print('connected_db=' + str(db))
        if str(db) == 'hiop_dev':
            print('REFUSE: current_database is hiop_dev')
            sys.exit(3)
        cur.execute('CREATE DATABASE IF NOT EXISTS hiop_agent_memory')
        print('CREATE_DATABASE_OK')
"@
$pyPath = Join-Path $env:TEMP "hiop_create_mem_db.py"
Set-Content -Path $pyPath -Value $py -Encoding UTF8
$env:TMP_CRDB_DEFAULT = $defaultUrl
python $pyPath
$code = $LASTEXITCODE
Remove-Item Env:TMP_CRDB_DEFAULT -ErrorAction SilentlyContinue
Remove-Item $pyPath -Force -ErrorAction SilentlyContinue
if ($code -ne 0) { throw "CREATE DATABASE failed (exit $code)" }

[Environment]::SetEnvironmentVariable("CRDB_DSN", $memUrl, "User")
[Environment]::SetEnvironmentVariable("CRDB_DSN", $memUrl, "Process")
$env:CRDB_DSN = $memUrl
Write-Host "CRDB_DSN set for this user and process to hiop_agent_memory (value not printed)."
Write-Host "You can close this window and tell Grok: DSN ready"
