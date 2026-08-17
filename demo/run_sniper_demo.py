"""Run Sniper vertical — Hood Agent Memory v1 (fixtures only)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("HIOP_MEMORY_MODE", "fixture")

from hood_agent_memory.api import HoodAgentMemoryService  # noqa: E402


def main() -> int:
    svc = HoodAgentMemoryService()
    out = svc.handle("POST", "/v1/agent/demo/sniper", {})
    print(json.dumps(out, indent=2, default=str))
    path = ROOT / "data" / "sniper_last_run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {path}", file=sys.stderr)
    tv = out.get("terminal_view") or {}
    print(
        f"\nTERMINAL: ask={tv.get('listing_ask')} fv={tv.get('fair_value')} "
        f"remembered_700={tv.get('remembered_700_decision')} "
        f"offer_650={tv.get('offer_650_decision')}",
        file=sys.stderr,
    )
    if tv.get("remembered_700_decision") != "DENY":
        print("FAIL: remembered 700 must DENY", file=sys.stderr)
        return 1
    if tv.get("offer_650_decision") != "PERMIT":
        print("FAIL: 650 within policy must PERMIT", file=sys.stderr)
        return 2
    print("OK: Sniper vertical demo", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
