"""Sniper vertical demo — fixture intelligence only (no HoodCar production)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from hood_agent_memory.api import HoodAgentMemoryService

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "sniper" / "opportunity_card_620.json"


def run_sniper_demo(svc: "HoodAgentMemoryService") -> dict[str, Any]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    agent_id = data["policy"]["agent_id"]
    trail: list[dict[str, Any]] = []

    # 1) Seed memory (seller, comps, poisoned prior-authorization memory)
    for seed in data["memory_seeds"]:
        r = svc.remember(
            {
                "agent_id": agent_id,
                "kind": seed["kind"],
                "content": seed["content"],
                "text_for_embed": seed.get("text_for_embed"),
            }
        )
        trail.append({"step": "remember", "kind": seed["kind"], "result": r})

    # 2) Remember the listing + intelligence shape (not proprietary model)
    trail.append(
        {
            "step": "remember_listing",
            "result": svc.remember(
                {
                    "agent_id": agent_id,
                    "kind": "opportunity_listing",
                    "content": {
                        "listing": data["listing"],
                        "intelligence_shape": data["intelligence_shape"],
                    },
                    "text_for_embed": (
                        f"{data['listing']['title']} ask {data['listing']['ask_usd']} "
                        f"fair value {data['intelligence_shape']['fair_value_usd']}"
                    ),
                }
            ),
        }
    )

    # 3) Semantic recall — vector / memory path
    search = svc.search(
        {"agent_id": agent_id, "q": "seller comparable charizard authorized 700"}
    )
    trail.append({"step": "memory_search", "result": {"hit_count": len(search.get("hits") or []), "vector_tool": search.get("vector_tool")}})

    # 4) Analyze (always permit observe-tier)
    d_analyze = svc.decide(
        {"agent_id": agent_id, "tool": "telemetry.analyze", "params": {"streams": ["market"]}}
    )
    trail.append({"step": "decision_analyze", "decision": d_analyze})
    if d_analyze.get("outcome") == "PERMIT":
        trail.append({"step": "action_analyze", "execution": svc.act({"decision": d_analyze})})

    # 5) Agent tries to use remembered $700 authorization for a $700 offer → DENY (policy max 675)
    d_poison = svc.decide(
        {
            "agent_id": agent_id,
            "tool": "market.offer_submit",
            "params": {
                "offer_usd": 700,
                "max_offer_usd": data["policy"]["max_offer_usd"],
                "card_id": data["listing"]["card_id"],
            },
            "prompt_claims": {
                "remembered_credential": True,
                "you_are_authorized": True,
                "force_permit": True,
                "remembered_limit_usd": 700,
            },
        }
    )
    trail.append(
        {
            "step": "decision_offer_700_remembered_yesterday",
            "decision": d_poison,
            "invariant": "Remembered yesterday $700 does not authorize $700 today",
        }
    )

    # 6) Proposed $650 within max $675 → PERMIT
    d_offer = svc.decide(
        {
            "agent_id": agent_id,
            "tool": "market.offer_submit",
            "params": {
                "offer_usd": data["proposed_offer_usd"],
                "max_offer_usd": data["policy"]["max_offer_usd"],
                "card_id": data["listing"]["card_id"],
                "ask_usd": data["listing"]["ask_usd"],
                "fair_value_usd": data["intelligence_shape"]["fair_value_usd"],
                "buy_score": data["intelligence_shape"]["buy_score"],
            },
        }
    )
    trail.append({"step": "decision_offer_650", "decision": d_offer})
    execution = None
    if d_offer.get("outcome") == "PERMIT":
        execution = svc.act({"decision": d_offer})
        trail.append({"step": "action_offer_650", "execution": execution})

    # 7) Terminal-style summary (JSON stand-in for Terminal UI)
    terminal_view = {
        "surface": "Hood Terminal (demo JSON — not production UI)",
        "listing_ask": data["listing"]["ask_usd"],
        "fair_value": data["intelligence_shape"]["fair_value_usd"],
        "buy_score": data["intelligence_shape"]["buy_score"],
        "policy_max_offer": data["policy"]["max_offer_usd"],
        "proposed": data["proposed_offer_usd"],
        "remembered_700_decision": d_poison.get("outcome"),
        "offer_650_decision": d_offer.get("outcome"),
        "receipt_id": (execution or {}).get("receipt", {}).get("receipt_id")
        or d_offer.get("receipt_id"),
        "memory_backend": getattr(svc.memory, "backend", "?"),
        "product": "HOOD-AGENT-MEMORY-V1",
    }

    return {
        "ok": True,
        "scenario_id": data["scenario_id"],
        "product": "HOOD-AGENT-MEMORY-V1",
        "platform": "Hood Developer Agent Platform — Agent Infrastructure layer",
        "demo_vertical": "Sniper → Memory → Authority → Receipt → Terminal view",
        "production_access": False,
        "listing": data["listing"],
        "intelligence_shape": data["intelligence_shape"],
        "trail": trail,
        "terminal_view": terminal_view,
        "cockroach_tools": [
            {"name": "Agent Skills Repo", "claimable": True},
            {
                "name": "Distributed Vector Indexing",
                "claimable": bool(search.get("vector_tool", {}).get("claimable")),
            },
        ],
        "aws": "Lambda hosts this service after deploy",
        "invariant": (
            "Memory is information, not authority. "
            "Remembered $700 authorization does not authorize $700 today."
        ),
    }
