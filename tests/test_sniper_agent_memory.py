"""Sniper vertical + Hood Agent Memory API tests (fixtures only)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["HIOP_MEMORY_MODE"] = "fixture"

from hood_agent_memory.api import HoodAgentMemoryService


def test_sniper_remembered_700_denied_650_permitted():
    svc = HoodAgentMemoryService()
    out = svc.handle("POST", "/v1/agent/demo/sniper", {})
    assert out["ok"] is True
    assert out["production_access"] is False
    tv = out["terminal_view"]
    assert tv["remembered_700_decision"] == "DENY"
    assert tv["offer_650_decision"] == "PERMIT"
    assert out["product"] == "HOOD-AGENT-MEMORY-V1"


def test_api_remember_search_decision():
    svc = HoodAgentMemoryService()
    r = svc.handle(
        "POST",
        "/v1/agent/memory",
        {"agent_id": "ops-memory-agent", "kind": "note", "content": {"x": 1}, "text_for_embed": "hello market"},
    )
    assert r["ok"] is True
    s = svc.handle("GET", "/v1/agent/memory/search", query={"q": "market", "agent_id": "ops-memory-agent"})
    assert s["ok"] is True
    d = svc.handle(
        "POST",
        "/v1/agent/decision",
        {"agent_id": "ops-memory-agent", "tool": "telemetry.analyze", "params": {}},
    )
    assert d["outcome"] == "PERMIT"
