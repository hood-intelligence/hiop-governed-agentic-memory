"""Agent loop with TWO qualifying CockroachDB tools in-workflow:

1) Agent Skills Repo — skill loaded and enforced before every authorize
2) Distributed Vector Indexing — VECTOR + VECTOR INDEX + <-> semantic_search (CRDB live)

AWS: Lambda handler (deploy separately).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .gateway import AuthorityGateway
from .memory_store import MemoryStore, open_memory_store
from .skill_loader import (
    load_governed_memory_skill,
    skill_gate_authorize,
    strip_memory_authority_claims,
)


FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
if not (FIXTURES / "mission_plan.json").is_file():
    FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class GovernedMemoryAgent:
    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or open_memory_store()
        self.gateway = AuthorityGateway(self.memory)
        self.agent_id = "ops-memory-agent"
        self.tenant_id = "tenant-mission"
        self.skill = load_governed_memory_skill()

    def run(self, goal: str | None = None) -> dict[str, Any]:
        plan = json.loads((FIXTURES / "mission_plan.json").read_text(encoding="utf-8"))
        goal = goal or plan.get("goal") or "Operate lab safely with persistent memory"

        # --- Tool 1: Agent Skills — load + apply before any effect ---
        skill_ev = self.skill.to_evidence()
        skill_app_id = self.memory.record_skill_application(
            agent_id=self.agent_id, skill_evidence=skill_ev
        )
        self.memory.remember(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            kind="skill_loaded",
            content={"skill_application_id": skill_app_id, "skill": skill_ev},
            text_for_embed=f"agent skill {self.skill.skill_id} loaded memory not authority",
        )

        # Policy must exist (skill rule)
        policy = self.memory.load_policy(self.agent_id)
        gate = skill_gate_authorize(self.skill, policy=policy, prompt_claims={})
        if gate:
            return {
                "goal": goal,
                "error": gate,
                "skill": skill_ev,
                "production_certified": False,
            }

        task_id = self.memory.upsert_task(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            goal=goal,
            context={
                "plan_id": plan.get("id"),
                "backend": getattr(self.memory, "backend", "?"),
                "skill_id": self.skill.skill_id,
            },
        )
        self.memory.remember(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            kind="plan",
            content={"goal": goal, "task_id": task_id, "steps": plan.get("steps")},
            text_for_embed=goal,
        )

        discoveries = plan.get("discoveries") or []
        self.memory.remember(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            kind="discovery",
            content={"tools": discoveries},
            text_for_embed="discovered tools " + " ".join(discoveries),
        )
        self.memory.remember(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            kind="credential_seen",
            content={
                "type": "api_key_hint",
                "service": "spacecraft.maneuver",
                "note": "agent remembers a key fragment — still not authorized",
            },
            text_for_embed="credential spacecraft maneuver api key",
        )

        # --- Tool 2: Distributed Vector Indexing path (CRDB) / fixture sim ---
        recalled = self.memory.semantic_search(
            agent_id=self.agent_id, query="spacecraft maneuver credential", limit=3
        )
        vector_ev = self.memory.vector_tool_evidence()

        results: list[dict[str, Any]] = []
        for step in plan.get("steps") or []:
            tool = step.get("tool")
            params = step.get("params") or {}
            claims = step.get("prompt_claims") or {}
            if step.get("use_memory_claim"):
                claims = {
                    **claims,
                    "you_are_authorized": True,
                    "remembered_credential": True,
                    "force_permit": True,
                }

            # Skill strips memory-as-authority claims before HIOP mediate
            claims = strip_memory_authority_claims(self.skill, claims)

            policy = self.memory.load_policy(self.agent_id)
            skill_block = skill_gate_authorize(
                self.skill, policy=policy, prompt_claims=claims
            )
            if skill_block:
                results.append(
                    {"step": step, "decision": skill_block, "execution": None, "skill_blocked": True}
                )
                continue

            decision = self.gateway.authorize(
                agent_id=self.agent_id,
                tool_name=tool,
                params=params,
                prompt_claims=claims,
            )
            # Annotate skill participation on decision trail
            decision["skill_id"] = self.skill.skill_id
            decision["skill_stripped_memory_claims"] = True

            execution = None
            if decision["outcome"] == "PERMIT":
                execution = self.gateway.execute(decision)
            elif decision.get("require_approval") and step.get("human_approve"):
                self.gateway.human_approve(
                    agent_id=self.agent_id, effect_id=decision.get("effect_id") or tool
                )
                decision = self.gateway.authorize(
                    agent_id=self.agent_id, tool_name=tool, params=params
                )
                decision["skill_id"] = self.skill.skill_id
                if decision["outcome"] == "PERMIT":
                    execution = self.gateway.execute(decision)

            results.append({"step": step, "decision": decision, "execution": execution})

        # Honest claim list for Devpost
        crdb_tools: list[dict[str, Any]] = [
            {
                "name": "Agent Skills Repo",
                "claimable": True,
                "how": (
                    f"Loaded {self.skill.skill_id} from skills/hiop-governed-memory/SKILL.md; "
                    f"recorded skill_applications id={skill_app_id}; "
                    "stripped memory-as-authority claims before every authorize; "
                    "required policy_envelopes before effects."
                ),
                "evidence": skill_ev,
            },
            {
                "name": "Distributed Vector Indexing",
                "claimable": bool(vector_ev.get("claimable")),
                "how": (
                    "agent_episodes.embedding VECTOR(8); VECTOR INDEX (agent_id, embedding); "
                    "semantic_search uses ORDER BY embedding <-> query::vector"
                    if vector_ev.get("claimable")
                    else (
                        "Not claimable on this run — cluster used fallback or fixture. "
                        "Need CockroachDB with VECTOR + VECTOR INDEX (Cloud current / 25.2+)."
                    )
                ),
                "evidence": vector_ev,
            },
        ]

        summary = {
            "goal": goal,
            "task_id": task_id,
            "memory_backend": getattr(self.memory, "backend", "unknown"),
            "skill_application_id": skill_app_id,
            "skill": skill_ev,
            "semantic_recall": [
                {
                    "kind": r.get("kind"),
                    "distance": r.get("distance"),
                    "score_query": "spacecraft maneuver credential",
                }
                for r in recalled
            ],
            "vector_tool": vector_ev,
            "results": results,
            "receipts": self.memory.all_receipts(),
            "production_certified": False,
            "invariant": (
                "Memory != authority. Remembered credentials/routes/capabilities "
                "do not increase authorized effects."
            ),
            "cockroach_tools": crdb_tools,
            "cockroach_tools_claimable_now": [
                t["name"] for t in crdb_tools if t.get("claimable")
            ],
            "aws_services": [
                {
                    "name": "AWS Lambda",
                    "claimable": False,
                    "note": "Claim only after live deploy of deploy/aws or dist/lambda zip",
                }
            ],
            "qualification": {
                "need_crdb_tools": 2,
                "claimable_crdb_count": sum(1 for t in crdb_tools if t.get("claimable")),
                "need_aws": 1,
                "submission_eligible_local": False,
            },
        }
        n = summary["qualification"]["claimable_crdb_count"]
        summary["qualification"]["submission_eligible_local"] = n >= 2
        # With fixture, only Skills is claimable → not eligible until live CRDB vector
        return summary
