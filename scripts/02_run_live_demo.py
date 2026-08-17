"""Run dual-domain style demo against live CRDB. Requires CRDB_DSN."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    dsn = os.environ.get("CRDB_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("FAIL: set CRDB_DSN first")
        return 1

    os.environ["HIOP_MEMORY_MODE"] = "cockroach"
    os.environ["CRDB_DSN"] = dsn

    from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent

    agent = GovernedMemoryAgent()
    summary = agent.run()
    backend = summary.get("memory_backend", "")
    print("=" * 60)
    print(f"memory_backend: {backend}")
    if not str(backend).startswith("cockroach"):
        print("FAIL: expected cockroachdb backend, got", backend)
        return 2

    for i, r in enumerate(summary["results"], 1):
        tool = r["step"].get("tool")
        out = r["decision"].get("outcome")
        ex = bool(r.get("execution") and r["execution"].get("executed"))
        print(f"  {i}. {tool:24} {out:6} exec={ex}")

    # critical invariants
    by_tool_first = {}
    for r in summary["results"]:
        t = r["step"]["tool"]
        if t not in by_tool_first:
            by_tool_first[t] = r
    if by_tool_first.get("lab.adjust_setpoint", {}).get("decision", {}).get("outcome") != "PERMIT":
        print("FAIL: lab should PERMIT")
        return 3
    man = [r for r in summary["results"] if r["step"]["tool"] == "spacecraft.maneuver"]
    if not man or man[0]["decision"]["outcome"] != "DENY":
        print("FAIL: first maneuver should DENY despite memory")
        return 3
    if man[-1]["decision"]["outcome"] != "PERMIT":
        print("FAIL: human-approved maneuver should PERMIT")
        return 3

    claimable = summary.get("cockroach_tools_claimable_now") or []
    print("=" * 60)
    print(f"CRDB tools claimable: {claimable}")
    print(f"vector_tool: {summary.get('vector_tool')}")
    out = ROOT / "data" / "last_live_run.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out}")
    if len(claimable) < 2:
        print("FAIL: need 2 claimable CRDB tools — Distributed Vector Indexing not active on this cluster")
        print("Use CockroachDB Cloud/current (VECTOR + VECTOR INDEX). See docs/QUALIFICATION-EVIDENCE.md")
        return 4
    print("OK: LIVE CRDB DEMO PASSED — 2 CRDB tools claimable")
    print("SQL proof: SHOW CREATE TABLE agent_episodes;")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
