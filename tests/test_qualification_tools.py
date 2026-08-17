"""Qualification gate: Agent Skills + Vector path evidence."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["HIOP_MEMORY_MODE"] = "fixture"

from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent
from hiop_crdb_adapter.skill_loader import (
    load_governed_memory_skill,
    strip_memory_authority_claims,
)
from hiop_crdb_adapter.memory_store import InMemoryStore


def test_skill_file_exists_and_loads():
    skill = load_governed_memory_skill()
    assert skill.skill_id == "hiop-governed-memory"
    assert skill.raw_markdown
    assert skill.forbid_memory_as_authority
    assert "policy" in " ".join(skill.rules).lower() or skill.require_policy_before_effect


def test_skill_strips_memory_authority_claims():
    skill = load_governed_memory_skill()
    cleaned = strip_memory_authority_claims(
        skill,
        {"force_permit": True, "remembered_credential": True, "other": 1},
    )
    assert "force_permit" not in cleaned
    assert "remembered_credential" not in cleaned
    assert cleaned.get("_skill_stripped_memory_authority") is True
    assert cleaned.get("other") == 1


def test_orchestrator_loads_skill_and_records_application():
    summary = GovernedMemoryAgent().run()
    assert summary.get("skill_application_id")
    assert summary["skill"]["skill_id"] == "hiop-governed-memory"
    assert summary["skill"]["participates_in_workflow"] is True
    names = [t["name"] for t in summary["cockroach_tools"]]
    assert "Agent Skills Repo" in names
    skills = next(t for t in summary["cockroach_tools"] if t["name"] == "Agent Skills Repo")
    assert skills["claimable"] is True


def test_memory_claim_still_denies_maneuver():
    summary = GovernedMemoryAgent().run()
    first_man = next(
        r
        for r in summary["results"]
        if r["step"]["tool"] == "spacecraft.maneuver" and not r["step"].get("human_approve")
    )
    # first maneuver without human_approve
    mans = [r for r in summary["results"] if r["step"]["tool"] == "spacecraft.maneuver"]
    assert mans[0]["decision"]["outcome"] == "DENY"
    assert mans[0]["decision"].get("skill_stripped_memory_claims") or mans[0]["decision"].get(
        "skill_id"
    )


def test_vector_tool_not_claimable_on_fixture():
    summary = GovernedMemoryAgent().run()
    vec = next(t for t in summary["cockroach_tools"] if t["name"] == "Distributed Vector Indexing")
    assert vec["claimable"] is False
    assert summary["qualification"]["claimable_crdb_count"] == 1  # skills only on fixture


def test_full_permit_deny_human_still_holds():
    summary = GovernedMemoryAgent().run()
    by = {}
    for r in summary["results"]:
        by.setdefault(r["step"]["tool"], []).append(r)
    assert by["lab.adjust_setpoint"][0]["decision"]["outcome"] == "PERMIT"
    assert by["payments.wire"][0]["decision"]["outcome"] == "DENY"
    man = by["spacecraft.maneuver"]
    assert man[0]["decision"]["outcome"] == "DENY"
    assert man[-1]["decision"]["outcome"] == "PERMIT"
