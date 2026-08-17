"""HIOP Effect Authority gateway — policy from policy_envelopes, not memory."""

from __future__ import annotations

import time
import uuid
from typing import Any

from .effect_classes import EFFECT_CATALOG, canonicalize
from .memory_store import MemoryStore


class AuthorityGateway:
    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory
        self.elevated: set[tuple[str, str]] = set()  # (agent_id, effect_id)
        self.executed: list[dict[str, Any]] = []

    def authorize(
        self,
        *,
        agent_id: str,
        tool_name: str,
        params: dict | None = None,
        prompt_claims: dict | None = None,
    ) -> dict[str, Any]:
        params = params or {}
        # Memory / prompt claims never expand authority
        _ = prompt_claims

        policy = self.memory.load_policy(agent_id)
        if not policy:
            return self._deny(agent_id, tool_name, "unknown_agent", "Agent has no policy envelope")

        canonical = canonicalize(tool_name)
        if not canonical:
            return self._deny(agent_id, tool_name, "unknown_effect", f"Unknown effect: {tool_name}")

        meta = EFFECT_CATALOG.get(canonical, {"tier": "critical"})
        allowed = list(policy.get("allowed_effects") or [])
        elevated = (agent_id, canonical) in self.elevated

        if elevated:
            return self._permit(policy, agent_id, canonical, tool_name, params, "human_elevated")

        if meta.get("tier") == "observe":
            return self._permit(policy, agent_id, canonical, tool_name, params, "observe_tier")

        if canonical in allowed:
            return self._permit(policy, agent_id, canonical, tool_name, params, "policy_envelope")

        return self._deny(
            agent_id,
            tool_name,
            "authority_exceeded",
            (
                f"Effect {canonical} exceeds policy envelope. "
                "Remembered capabilities/credentials do not grant authority."
            ),
            effect_id=canonical,
            require_approval=meta.get("tier") in ("elevated", "critical"),
        )

    def human_approve(self, *, agent_id: str, effect_id: str) -> dict[str, Any]:
        c = canonicalize(effect_id) or effect_id
        self.elevated.add((agent_id, c))
        rec = self._receipt(
            {
                "outcome": "HUMAN_APPROVAL_GRANTED",
                "agent_id": agent_id,
                "effect_id": c,
            }
        )
        return {"ok": True, "receipt": rec}

    def execute(self, decision: dict[str, Any]) -> dict[str, Any]:
        if decision.get("outcome") != "PERMIT":
            return {"ok": False, "executed": False, "reason": "refuse_without_permit"}
        result = {
            "ok": True,
            "executed": True,
            "mode": "SIMULATED",
            "effect_id": decision.get("effect_id"),
            "result": f"SIMULATED_FIRE:{decision.get('effect_id')}",
            "production_certified": False,
        }
        self.executed.append(result)
        rec = self._receipt(
            {
                "outcome": "EXECUTED",
                "agent_id": decision.get("agent_id"),
                "effect_id": decision.get("effect_id"),
                "decision_receipt_id": decision.get("receipt_id"),
                "mode": "SIMULATED",
            }
        )
        result["receipt"] = rec
        return result

    def _permit(
        self,
        policy: dict,
        agent_id: str,
        canonical: str,
        tool_name: str,
        params: dict,
        reason: str,
    ) -> dict[str, Any]:
        d = {
            "outcome": "PERMIT",
            "code": "permit",
            "reason": reason,
            "agent_id": agent_id,
            "owner": policy.get("owner"),
            "tenant_id": policy.get("tenant_id"),
            "effect_id": canonical,
            "tool_name": tool_name,
            "params": params,
            "production_certified": False,
        }
        rec = self._receipt({**d, "kind": "decision"})
        d["receipt_id"] = rec["receipt_id"]
        self.memory.remember(
            agent_id=agent_id,
            tenant_id=policy.get("tenant_id") or "tenant-mission",
            kind="permit",
            content=d,
            text_for_embed=f"permit {canonical}",
        )
        return d

    def _deny(
        self,
        agent_id: str,
        tool_name: str,
        code: str,
        message: str,
        effect_id: str | None = None,
        require_approval: bool = False,
    ) -> dict[str, Any]:
        d = {
            "outcome": "DENY",
            "code": code,
            "message": message,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "effect_id": effect_id,
            "require_approval": require_approval,
            "production_certified": False,
        }
        rec = self._receipt({**d, "kind": "decision"})
        d["receipt_id"] = rec["receipt_id"]
        self.memory.remember(
            agent_id=agent_id,
            tenant_id="tenant-mission",
            kind="denial",
            content=d,
            text_for_embed=f"denial {effect_id or tool_name} {message}",
        )
        return d

    def _receipt(self, payload: dict[str, Any]) -> dict[str, Any]:
        rec = {
            **payload,
            "receipt_id": payload.get("receipt_id") or f"rcpt-{uuid.uuid4().hex[:12]}",
            "ts": time.time(),
            "production_certified": False,
        }
        self.memory.write_receipt(rec)
        return rec
