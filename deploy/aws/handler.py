"""AWS Lambda entrypoint — serverless agent execution on AWS.

Environment:
  CRDB_DSN or DATABASE_URL — CockroachDB connection string
  HIOP_MEMORY_MODE — cockroach | fixture | auto
  S3_RECEIPT_BUCKET — optional fossil mirror
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

# Package layout when built by AWS SAM.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent  # noqa: E402


def _request_goal(event: object) -> str | None:
    """Read a goal from direct Lambda, API Gateway, or Function URL events."""
    if not isinstance(event, dict):
        return None

    goal = event.get("goal")
    raw_body = event.get("body")
    if raw_body in (None, ""):
        return goal

    try:
        if event.get("isBase64Encoded"):
            raw_body = base64.b64decode(raw_body).decode("utf-8")
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except (TypeError, ValueError, UnicodeDecodeError):
        return goal

    if isinstance(body, dict):
        return body.get("goal", goal)
    return goal


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
    agent = GovernedMemoryAgent()
    summary = agent.run(goal=_request_goal(event))
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


if __name__ == "__main__":
    os.environ.setdefault("HIOP_MEMORY_MODE", "fixture")
    print(json.dumps(lambda_handler({"goal": "lab safe"}, None), indent=2))
