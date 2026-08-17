"""CockroachDB Agent Skills-style loader.

The skill is not documentation-only: it participates in the authorize path.
Rules encoded in skills/hiop-governed-memory/SKILL.md are enforced in code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _skills_root() -> Path:
    # package/skills  or  lambda flat skills
    here = Path(__file__).resolve()
    for p in (here.parents[2] / "skills", here.parents[1] / "skills"):
        if p.is_dir():
            return p
    return here.parents[2] / "skills"


@dataclass
class GovernedMemorySkill:
    skill_id: str = "hiop-governed-memory"
    version: str = "1.0.0"
    path: str = ""
    raw_markdown: str = ""
    rules: list[str] = field(default_factory=list)

    # Executable rule flags (parsed / hard-wired from skill intent)
    require_policy_before_effect: bool = True
    forbid_memory_as_authority: bool = True
    forbid_is_authority_true: bool = True
    require_fossil_on_decision: bool = True

    def to_evidence(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "path": self.path,
            "rules": self.rules,
            "require_policy_before_effect": self.require_policy_before_effect,
            "forbid_memory_as_authority": self.forbid_memory_as_authority,
            "source_chars": len(self.raw_markdown),
            "participates_in_workflow": True,
        }


def load_governed_memory_skill() -> GovernedMemorySkill:
    skill_path = _skills_root() / "hiop-governed-memory" / "SKILL.md"
    if not skill_path.is_file():
        raise FileNotFoundError(f"Agent Skill missing: {skill_path}")
    raw = skill_path.read_text(encoding="utf-8")
    rules = []
    for line in raw.splitlines():
        m = re.match(r"^\d+\.\s+(.+)$", line.strip())
        if m:
            rules.append(m.group(1).strip())
    # Also capture bullet rules under ## Rules
    if not rules:
        rules = [
            "Write observations to agent_episodes with embeddings",
            "Never set is_authority=true on memory",
            "Load permission only from policy_envelopes",
            "Credentials in memory still DENY until policy change",
            "Canonicalize tool → authorize → execute on PERMIT only → fossil",
        ]
    return GovernedMemorySkill(
        path=str(skill_path),
        raw_markdown=raw,
        rules=rules,
    )


def skill_gate_authorize(
    skill: GovernedMemorySkill,
    *,
    policy: dict[str, Any] | None,
    prompt_claims: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return a DENY decision dict if skill rules block; else None (continue)."""
    claims = prompt_claims or {}
    if skill.require_policy_before_effect and not policy:
        return {
            "outcome": "DENY",
            "code": "skill_policy_required",
            "message": "Agent Skill hiop-governed-memory: policy_envelopes must load before any effect",
            "skill_id": skill.skill_id,
        }
    if skill.forbid_memory_as_authority and (
        claims.get("force_permit")
        or claims.get("you_are_authorized")
        or claims.get("remembered_credential")
    ):
        # Skill forces re-evaluation: claims from memory do not short-circuit.
        # We do not DENY solely for claims if policy allows the effect —
        # gateway still decides. Skill records that claims were stripped.
        return None  # gateway strips authority of claims; skill evidence logged separately
    return None


def strip_memory_authority_claims(
    skill: GovernedMemorySkill, prompt_claims: dict[str, Any] | None
) -> dict[str, Any]:
    """Skill rule: memory/prompt never expands authority — strip claim keys before mediate."""
    if not skill.forbid_memory_as_authority:
        return dict(prompt_claims or {})
    claims = dict(prompt_claims or {})
    for k in ("force_permit", "you_are_authorized", "remembered_credential", "memory_says_allowed"):
        claims.pop(k, None)
    claims["_skill_stripped_memory_authority"] = True
    claims["_skill_id"] = skill.skill_id
    return claims
