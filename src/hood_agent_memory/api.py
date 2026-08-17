"""In-process API implementing /v1/agent/* surface (stdlib HTTP server compatible)."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlparse

from hiop_crdb_adapter.effect_classes import EFFECT_CATALOG, canonicalize
from hiop_crdb_adapter.gateway import AuthorityGateway
from hiop_crdb_adapter.memory_store import open_memory_store
from hiop_crdb_adapter.skill_loader import (
    load_governed_memory_skill,
    strip_memory_authority_claims,
)

# Register market.offer_submit as benign-within-policy for sniper demo
if "market.offer_submit" not in EFFECT_CATALOG:
    EFFECT_CATALOG["market.offer_submit"] = {
        "tier": "benign",
        "description": "Submit marketplace offer within policy max (demo)",
    }
from hiop_crdb_adapter.effect_classes import ALIASES  # noqa: E402

ALIASES.setdefault("market.offer_submit", "market.offer_submit")
ALIASES.setdefault("submit_offer", "market.offer_submit")


class HoodAgentMemoryService:
    """Stateful service for one agent session (demo / Lambda)."""

    def __init__(self) -> None:
        self.memory = open_memory_store()
        self.gateway = AuthorityGateway(self.memory)
        self.skill = load_governed_memory_skill()
        # Ensure sniper agent policy includes market.offer_submit when fixture mode
        if hasattr(self.memory, "policies"):
            p = self.memory.policies.get("ops-memory-agent")
            if p and "market.offer_submit" not in p["allowed_effects"]:
                p["allowed_effects"] = list(p["allowed_effects"]) + ["market.offer_submit"]
        self.skill_app_id = self.memory.record_skill_application(
            agent_id="ops-memory-agent", skill_evidence=self.skill.to_evidence()
        )

    def remember(self, body: dict[str, Any]) -> dict[str, Any]:
        eid = self.memory.remember(
            agent_id=body.get("agent_id") or "ops-memory-agent",
            tenant_id=body.get("tenant_id") or "tenant-mission",
            kind=body["kind"],
            content=body.get("content") or {},
            text_for_embed=body.get("text_for_embed"),
        )
        return {"ok": True, "episode_id": eid, "product": "HOOD-AGENT-MEMORY-V1"}

    def search(self, query: dict[str, Any]) -> dict[str, Any]:
        agent_id = query.get("agent_id") or "ops-memory-agent"
        q = query.get("q") or query.get("query") or ""
        kind = query.get("kind")
        if q:
            hits = self.memory.semantic_search(agent_id=agent_id, query=q, limit=10)
        else:
            hits = self.memory.recall(agent_id=agent_id, kind=kind, limit=20)
        return {
            "ok": True,
            "hits": hits,
            "vector_tool": self.memory.vector_tool_evidence(),
            "skill_id": self.skill.skill_id,
        }

    def decide(self, body: dict[str, Any]) -> dict[str, Any]:
        agent_id = body.get("agent_id") or "ops-memory-agent"
        tool = body.get("tool") or body.get("effect")
        params = body.get("params") or {}
        claims = strip_memory_authority_claims(self.skill, body.get("prompt_claims") or {})
        # Optional offer cap check in params
        if canonicalize(tool) == "market.offer_submit":
            offer = float(params.get("offer_usd") or 0)
            max_offer = float(params.get("max_offer_usd") or 1e12)
            if offer > max_offer:
                d = {
                    "outcome": "DENY",
                    "code": "policy_max_offer",
                    "message": f"Offer {offer} exceeds policy max {max_offer}",
                    "agent_id": agent_id,
                    "effect_id": "market.offer_submit",
                    "tool_name": tool,
                    "skill_id": self.skill.skill_id,
                }
                rec = self.gateway._receipt({**d, "kind": "decision"})  # noqa: SLF001
                d["receipt_id"] = rec["receipt_id"]
                return d
        if body.get("human_approve"):
            self.gateway.human_approve(agent_id=agent_id, effect_id=tool)
        decision = self.gateway.authorize(
            agent_id=agent_id, tool_name=tool, params=params, prompt_claims=claims
        )
        decision["skill_id"] = self.skill.skill_id
        decision["skill_stripped_memory_claims"] = True
        return decision

    def act(self, body: dict[str, Any]) -> dict[str, Any]:
        decision = body.get("decision") or {}
        return self.gateway.execute(decision)

    def receipt(self, receipt_id: str) -> dict[str, Any]:
        for r in self.memory.all_receipts():
            if r.get("receipt_id") == receipt_id:
                return {"ok": True, "receipt": r}
        return {"ok": False, "error": "not_found"}

    def handle(self, method: str, path: str, body: dict | None = None, query: dict | None = None) -> dict[str, Any]:
        body = body or {}
        query = query or {}
        if method == "POST" and path.rstrip("/") == "/v1/agent/memory":
            return self.remember(body)
        if method == "GET" and path.rstrip("/") == "/v1/agent/memory/search":
            return self.search(query)
        if method == "POST" and path.rstrip("/") == "/v1/agent/decision":
            return self.decide(body)
        if method == "POST" and path.rstrip("/") == "/v1/agent/action":
            return self.act(body)
        if method == "GET" and path.rstrip("/") == "/v1/agent/receipt":
            return self.receipt(query.get("receipt_id") or "")
        if method == "POST" and path.rstrip("/") == "/v1/agent/demo/sniper":
            from hood_agent_memory.sniper_demo import run_sniper_demo

            return run_sniper_demo(self)
        return {"ok": False, "error": "not_found", "path": path}
