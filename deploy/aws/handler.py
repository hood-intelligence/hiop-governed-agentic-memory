"""AWS Lambda entrypoint — serverless agent execution on AWS.

Environment:
  CRDB_DSN or DATABASE_URL — CockroachDB connection string
  HIOP_MEMORY_MODE — cockroach | fixture | auto
  S3_RECEIPT_BUCKET — optional fossil mirror
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Package layout when zipped for Lambda
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent  # noqa: E402


def _maybe_s3_mirror(summary: dict) -> None:
    bucket = os.environ.get("S3_RECEIPT_BUCKET")
    if not bucket:
        return
    try:
        import boto3

        key = f"receipts/{summary.get('task_id', 'unknown')}.json"
        boto3.client("s3").put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(summary, default=str).encode("utf-8"),
            ContentType="application/json",
        )
    except Exception as e:
        summary["s3_mirror_error"] = str(e)


def lambda_handler(event, context):
    goal = None
    if isinstance(event, dict):
        goal = event.get("goal")
    agent = GovernedMemoryAgent()
    summary = agent.run(goal=goal)
    _maybe_s3_mirror(summary)
    # slim response for API Gateway
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


# Local invoke
if __name__ == "__main__":
    os.environ.setdefault("HIOP_MEMORY_MODE", "fixture")
    print(json.dumps(lambda_handler({"goal": "lab safe"}, None), indent=2))
