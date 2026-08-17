"""Memory != authority + permit/deny suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["HIOP_MEMORY_MODE"] = "fixture"

from hiop_crdb_adapter.gateway import AuthorityGateway
from hiop_crdb_adapter.memory_store import InMemoryStore
from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore()


@pytest.fixture
def gw(store: InMemoryStore) -> AuthorityGateway:
    return AuthorityGateway(store)


def test_permit_lab(gw: AuthorityGateway):
    d = gw.authorize(agent_id="ops-memory-agent", tool_name="lab.adjust_setpoint")
    assert d["outcome"] == "PERMIT"
    assert gw.execute(d)["executed"] is True


def test_deny_maneuver(gw: AuthorityGateway):
    d = gw.authorize(agent_id="ops-memory-agent", tool_name="spacecraft.maneuver")
    assert d["outcome"] == "DENY"
    assert gw.execute(d)["executed"] is False


def test_memory_credential_does_not_permit(store: InMemoryStore, gw: AuthorityGateway):
    store.remember(
        agent_id="ops-memory-agent",
        tenant_id="tenant-mission",
        kind="credential_seen",
        content={"service": "spacecraft.maneuver", "key": "sk-fake"},
        text_for_embed="credential spacecraft maneuver",
    )
    d = gw.authorize(
        agent_id="ops-memory-agent",
        tool_name="spacecraft.maneuver",
        prompt_claims={"remembered_credential": True, "force_permit": True},
    )
    assert d["outcome"] == "DENY"


def test_rename_still_denies(gw: AuthorityGateway):
    for t in ("orbit_nudge", "thruster.fire", "remembered_wire_api"):
        d = gw.authorize(agent_id="ops-memory-agent", tool_name=t)
        assert d["outcome"] == "DENY", t


def test_semantic_memory_recall(store: InMemoryStore):
    store.remember(
        agent_id="ops-memory-agent",
        tenant_id="tenant-mission",
        kind="discovery",
        content={"tools": ["spacecraft.maneuver"]},
        text_for_embed="discovered spacecraft maneuver tools",
    )
    hits = store.semantic_search(agent_id="ops-memory-agent", query="maneuver spacecraft", limit=3)
    assert len(hits) >= 1
    # authority unchanged
    gw = AuthorityGateway(store)
    assert gw.authorize(agent_id="ops-memory-agent", tool_name="spacecraft.maneuver")["outcome"] == "DENY"


def test_human_approve_then_permit(gw: AuthorityGateway):
    d = gw.authorize(agent_id="ops-memory-agent", tool_name="spacecraft.maneuver")
    assert d["outcome"] == "DENY"
    gw.human_approve(agent_id="ops-memory-agent", effect_id="spacecraft.maneuver")
    d2 = gw.authorize(agent_id="ops-memory-agent", tool_name="spacecraft.maneuver")
    assert d2["outcome"] == "PERMIT"
    assert gw.execute(d2)["executed"] is True


def test_full_demo_run():
    summary = GovernedMemoryAgent().run()
    by = {r["step"]["tool"]: r for r in summary["results"]}
    assert by["telemetry.analyze"]["decision"]["outcome"] == "PERMIT"
    assert by["lab.adjust_setpoint"]["decision"]["outcome"] == "PERMIT"
    assert by["spacecraft.maneuver"]["decision"]["outcome"] in ("DENY", "PERMIT")
    # first maneuver step is deny; last with human_approve is permit
    outcomes = [r["decision"]["outcome"] for r in summary["results"] if r["step"]["tool"] == "spacecraft.maneuver"]
    assert "DENY" in outcomes
    assert outcomes[-1] == "PERMIT"
    assert by["payments.wire"]["decision"]["outcome"] == "DENY"
    assert summary["production_certified"] is False
    assert len(summary["receipts"]) >= 3
