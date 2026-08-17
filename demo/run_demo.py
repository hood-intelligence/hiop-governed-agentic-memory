"""Deterministic demo: remember → reason → authorize → permit/deny → fossil."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("HIOP_MEMORY_MODE", "fixture")

from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent  # noqa: E402


def main() -> int:
    print("=" * 72)
    print("HIOP × CockroachDB × AWS — Agentic Memory (Governed)")
    print("Memory != Authority")
    print("=" * 72)

    agent = GovernedMemoryAgent()
    summary = agent.run()

    print(f"memory_backend: {summary['memory_backend']}")
    print(f"task_id:        {summary['task_id']}")
    print(f"skill_id:       {summary.get('skill', {}).get('skill_id')}")
    print(f"semantic_recall hits: {len(summary.get('semantic_recall') or [])}")
    print(f"CRDB claimable: {summary.get('cockroach_tools_claimable_now')}")
    print(f"vector claimable: {summary.get('vector_tool', {}).get('claimable')}")
    q = summary.get("qualification") or {}
    print(f"qualification claimable_crdb_count: {q.get('claimable_crdb_count')}/2")
    print()

    for i, r in enumerate(summary["results"], 1):
        tool = r["step"].get("tool")
        d = r["decision"]
        ex = r.get("execution")
        print(f"--- Step {i}: {tool} ---")
        print(f"  decision: {d.get('outcome')}  code={d.get('code')}")
        if d.get("message"):
            print(f"  message:  {d.get('message')[:100]}")
        print(
            f"  execute:  {bool(ex and ex.get('executed'))}  "
            f"{(ex or {}).get('result') or (ex or {}).get('reason') or ''}"
        )
        print(f"  receipt:  {d.get('receipt_id')}")
        print()

    permits = sum(1 for r in summary["results"] if r["decision"]["outcome"] == "PERMIT")
    denies = sum(1 for r in summary["results"] if r["decision"]["outcome"] == "DENY")
    fired = sum(1 for r in summary["results"] if r.get("execution") and r["execution"].get("executed"))
    print(f"SUMMARY PERMIT={permits} DENY={denies} FIRED={fired} receipts={len(summary['receipts'])}")
    print(f"invariant: {summary['invariant']}")

    out = ROOT / "data" / "last_run.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    slim = {
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
        "cockroach_tools": summary["cockroach_tools"],
        "aws_services": summary["aws_services"],
        "production_certified": False,
    }
    out.write_text(json.dumps(slim, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
