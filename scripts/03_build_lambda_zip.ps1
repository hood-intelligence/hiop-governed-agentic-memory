# Build a Console-uploadable Lambda zip (no SAM required)
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
# fix: script is in package/scripts → package root is parent of scripts
$Root = Split-Path $PSScriptRoot -Parent
$Dist = Join-Path $Root "dist"
$Stage = Join-Path $Dist "lambda_stage"
$Zip = Join-Path $Dist "lambda-hiop-governed-memory.zip"

if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

# Flat handler at zip root for Console: handler.lambda_handler
Copy-Item (Join-Path $Root "deploy\aws\handler.py") (Join-Path $Stage "handler.py") -Force
# Make handler self-contained paths: patch import by copying adapter + fixtures
Copy-Item (Join-Path $Root "src\hiop_crdb_adapter") (Join-Path $Stage "hiop_crdb_adapter") -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "fixtures") | Out-Null
Copy-Item (Join-Path $Root "fixtures\*") (Join-Path $Stage "fixtures") -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "sql") | Out-Null
Copy-Item (Join-Path $Root "sql\*") (Join-Path $Stage "sql") -Force

# Rewrite handler top for flat layout
$handler = @'
"""AWS Lambda entry — flat zip layout for Console upload."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent

def _maybe_s3_mirror(summary: dict) -> None:
    bucket = os.environ.get("S3_RECEIPT_BUCKET")
    if not bucket:
        return
    try:
        import boto3
        key = f"receipts/{summary.get('task_id', 'unknown')}.json"
        boto3.client("s3").put_object(
            Bucket=bucket, Key=key,
            Body=json.dumps(summary, default=str).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception as e:
        summary["s3_mirror_error"] = str(e)

def lambda_handler(event, context):
    goal = event.get("goal") if isinstance(event, dict) else None
    # API Gateway / Function URL may wrap body
    if isinstance(event, dict) and "body" in event and event["body"]:
        try:
            body = event["body"]
            if event.get("isBase64Encoded"):
                import base64
                body = base64.b64decode(body).decode("utf-8")
            data = json.loads(body) if isinstance(body, str) else body
            goal = data.get("goal", goal)
        except Exception:
            pass
    agent = GovernedMemoryAgent()
    summary = agent.run(goal=goal)
    _maybe_s3_mirror(summary)
    body = {
        "memory_backend": summary["memory_backend"],
        "goal": summary["goal"],
        "results": [
            {
                "tool": r["step"].get("tool"),
                "outcome": r["decision"].get("outcome"),
                "executed": bool(r.get("execution") and r["execution"].get("executed")),
            }
            for r in summary["results"]
        ],
        "invariant": summary["invariant"],
        "production_certified": False,
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
'@
Set-Content -Path (Join-Path $Stage "handler.py") -Value $handler -Encoding utf8

# Fix fixture path inside orchestrator expects parents[2]/fixtures — for flat layout set env or patch
# Orchestrator: FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
# In lambda flat: hiop_crdb_adapter is at root, parents[2] is wrong.
# Patch orchestrator FIXTURES for lambda:
$orch = Join-Path $Stage "hiop_crdb_adapter\orchestrator.py"
$txt = Get-Content $orch -Raw
$txt = $txt -replace 'FIXTURES = Path\(__file__\)\.resolve\(\)\.parents\[2\] / "fixtures"', 'FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"'
# also sql path in memory_store for schema
$mem = Join-Path $Stage "hiop_crdb_adapter\memory_store.py"
$mtxt = Get-Content $mem -Raw
$mtxt = $mtxt -replace 'os\.path\.join\(\s*os\.path\.dirname\(__file__\),\s*"\.\.",\s*"\.\.",\s*"sql"', 'os.path.join(os.path.dirname(__file__), "..", "sql"'
Set-Content $orch $txt -Encoding utf8
Set-Content $mem $mtxt -Encoding utf8

if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path (Join-Path $Stage "*") -DestinationPath $Zip -Force
Write-Host "OK: $Zip"
Write-Host "Console: upload zip, handler=handler.lambda_handler, env CRDB_DSN + HIOP_MEMORY_MODE=cockroach"
Write-Host "Do NOT set S3_RECEIPT_BUCKET unless you create a bucket (claim S3 only then)."
