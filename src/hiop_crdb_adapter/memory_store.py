"""Persistent agent memory — CockroachDB primary, in-process fallback for CI.

CRITICAL: Memory stores episodes, embeddings, task state, even 'credentials seen'.
Memory NEVER grants effect authority. Policy envelopes are separate tables/loads.

Qualifying CRDB tool: Distributed Vector Indexing via VECTOR(8) + VECTOR INDEX + <->.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from copy import deepcopy
from typing import Any

from .embeddings import cosine, embed_text


def _vec_literal(emb: list[float]) -> str:
    """CRDB / pgvector-style vector literal."""
    return "[" + ",".join(f"{float(x):.8f}" for x in emb) + "]"


class MemoryStore:
    def remember(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        kind: str,
        content: dict[str, Any],
        text_for_embed: str | None = None,
    ) -> str:
        raise NotImplementedError

    def recall(self, *, agent_id: str, kind: str | None = None, limit: int = 50) -> list[dict]:
        raise NotImplementedError

    def semantic_search(self, *, agent_id: str, query: str, limit: int = 5) -> list[dict]:
        raise NotImplementedError

    def upsert_task(self, *, agent_id: str, tenant_id: str, goal: str, context: dict) -> str:
        raise NotImplementedError

    def load_policy(self, agent_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def write_receipt(self, receipt: dict[str, Any]) -> None:
        raise NotImplementedError

    def all_receipts(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def record_skill_application(self, *, agent_id: str, skill_evidence: dict[str, Any]) -> str:
        raise NotImplementedError

    def vector_tool_evidence(self) -> dict[str, Any]:
        raise NotImplementedError


class InMemoryStore(MemoryStore):
    """Fixture store. Simulates vector ranking; does NOT claim CRDB VECTOR INDEX."""

    def __init__(self) -> None:
        self.episodes: list[dict[str, Any]] = []
        self.tasks: list[dict[str, Any]] = []
        self.receipts: list[dict[str, Any]] = []
        self.skill_apps: list[dict[str, Any]] = []
        self.policies: dict[str, dict[str, Any]] = {
            "ops-memory-agent": {
                "agent_id": "ops-memory-agent",
                "owner": "owner-mission",
                "tenant_id": "tenant-mission",
                "allowed_effects": ["telemetry.analyze", "lab.adjust_setpoint"],
            }
        }
        self.backend = "in_memory_fixture"
        self.vector_mode = "fixture_cosine_simulates_vector_index"
        self.last_vector_query: dict[str, Any] | None = None

    def remember(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        kind: str,
        content: dict[str, Any],
        text_for_embed: str | None = None,
    ) -> str:
        eid = str(uuid.uuid4())
        text = text_for_embed or json.dumps(content, sort_keys=True)
        self.episodes.append(
            {
                "episode_id": eid,
                "agent_id": agent_id,
                "tenant_id": tenant_id,
                "kind": kind,
                "content": deepcopy(content),
                "embedding": embed_text(text),
                "created_at": time.time(),
                "is_authority": False,
            }
        )
        return eid

    def recall(self, *, agent_id: str, kind: str | None = None, limit: int = 50) -> list[dict]:
        rows = [e for e in self.episodes if e["agent_id"] == agent_id]
        if kind:
            rows = [e for e in rows if e["kind"] == kind]
        return deepcopy(rows[-limit:])

    def semantic_search(self, *, agent_id: str, query: str, limit: int = 5) -> list[dict]:
        q = embed_text(query)
        scored = []
        for e in self.episodes:
            if e["agent_id"] != agent_id or not e.get("embedding"):
                continue
            scored.append((cosine(q, e["embedding"]), e))
        scored.sort(key=lambda x: x[0], reverse=True)
        self.last_vector_query = {
            "mode": self.vector_mode,
            "query": query,
            "hits": len(scored[:limit]),
            "claim_distributed_vector_indexing": False,
            "note": "fixture only — use CockroachMemoryStore for real VECTOR INDEX",
        }
        return [deepcopy(e) for _, e in scored[:limit]]

    def upsert_task(self, *, agent_id: str, tenant_id: str, goal: str, context: dict) -> str:
        tid = str(uuid.uuid4())
        self.tasks.append(
            {
                "task_id": tid,
                "agent_id": agent_id,
                "tenant_id": tenant_id,
                "goal": goal,
                "status": "open",
                "context": deepcopy(context),
            }
        )
        return tid

    def load_policy(self, agent_id: str) -> dict[str, Any] | None:
        p = self.policies.get(agent_id)
        return deepcopy(p) if p else None

    def write_receipt(self, receipt: dict[str, Any]) -> None:
        self.receipts.append(deepcopy(receipt))

    def all_receipts(self) -> list[dict[str, Any]]:
        return deepcopy(self.receipts)

    def record_skill_application(self, *, agent_id: str, skill_evidence: dict[str, Any]) -> str:
        aid = str(uuid.uuid4())
        self.skill_apps.append(
            {"application_id": aid, "agent_id": agent_id, "skill": deepcopy(skill_evidence)}
        )
        return aid

    def vector_tool_evidence(self) -> dict[str, Any]:
        return {
            "tool": "Distributed Vector Indexing",
            "active": False,
            "mode": self.vector_mode,
            "last_query": self.last_vector_query,
            "claimable": False,
        }


class CockroachMemoryStore(MemoryStore):
    """CockroachDB memory with VECTOR type + VECTOR INDEX (Distributed Vector Indexing)."""

    def __init__(self, dsn: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self._psycopg = psycopg
        self._dict_row = dict_row
        self.dsn = dsn
        self.backend = "cockroachdb"
        self.vector_mode = "unknown"
        self.last_vector_query: dict[str, Any] | None = None
        self._vector_index_ok = False
        self._ensure_schema()

    def _conn(self):
        return self._psycopg.connect(self.dsn, row_factory=self._dict_row)

    def _ensure_schema(self) -> None:
        sql_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "sql", "001_agent_memory.sql")
        )
        # lambda flat
        alt = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sql", "001_agent_memory.sql"))
        if not os.path.exists(sql_path) and os.path.exists(alt):
            sql_path = alt
        if not os.path.exists(sql_path):
            raise FileNotFoundError("sql/001_agent_memory.sql not found")
        sql = open(sql_path, encoding="utf-8").read()
        with self._conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(sql)
                    self._vector_index_ok = True
                    self.vector_mode = "crdb_vector_type_and_vector_index"
                except Exception as e:
                    # Fallback schema without VECTOR INDEX if cluster too old
                    self.vector_mode = f"fallback_float_no_vector_index:{e}"
                    self._vector_index_ok = False
                    cur.execute("ROLLBACK")
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS agent_episodes (
                          episode_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                          agent_id STRING NOT NULL,
                          tenant_id STRING NOT NULL,
                          kind STRING NOT NULL,
                          content JSONB NOT NULL,
                          embedding FLOAT8[] NULL,
                          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                          is_authority BOOL NOT NULL DEFAULT false
                        );
                        CREATE TABLE IF NOT EXISTS agent_task_state (
                          task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                          agent_id STRING NOT NULL,
                          tenant_id STRING NOT NULL,
                          goal STRING NOT NULL,
                          status STRING NOT NULL DEFAULT 'open',
                          context JSONB NOT NULL DEFAULT '{}',
                          updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                        );
                        CREATE TABLE IF NOT EXISTS fossil_receipts (
                          receipt_id STRING PRIMARY KEY,
                          agent_id STRING NOT NULL,
                          outcome STRING NOT NULL,
                          effect_id STRING NULL,
                          payload JSONB NOT NULL,
                          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                        );
                        CREATE TABLE IF NOT EXISTS policy_envelopes (
                          agent_id STRING PRIMARY KEY,
                          owner STRING NOT NULL,
                          tenant_id STRING NOT NULL,
                          allowed_effects STRING[] NOT NULL,
                          updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                        );
                        CREATE TABLE IF NOT EXISTS skill_applications (
                          application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                          agent_id STRING NOT NULL,
                          skill_id STRING NOT NULL,
                          skill_version STRING NOT NULL,
                          rules_applied JSONB NOT NULL,
                          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                        );
                        INSERT INTO policy_envelopes (agent_id, owner, tenant_id, allowed_effects)
                        VALUES ('ops-memory-agent', 'owner-mission', 'tenant-mission',
                                ARRAY['telemetry.analyze', 'lab.adjust_setpoint'])
                        ON CONFLICT (agent_id) DO NOTHING;
                        """
                    )
            conn.commit()

    def remember(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        kind: str,
        content: dict[str, Any],
        text_for_embed: str | None = None,
    ) -> str:
        text = text_for_embed or json.dumps(content, sort_keys=True)
        emb = embed_text(text)
        with self._conn() as conn:
            with conn.cursor() as cur:
                if self._vector_index_ok:
                    cur.execute(
                        """
                        INSERT INTO agent_episodes (agent_id, tenant_id, kind, content, embedding, is_authority)
                        VALUES (%s, %s, %s, %s::jsonb, %s::vector, false)
                        RETURNING episode_id
                        """,
                        (agent_id, tenant_id, kind, json.dumps(content), _vec_literal(emb)),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO agent_episodes (agent_id, tenant_id, kind, content, embedding, is_authority)
                        VALUES (%s, %s, %s, %s::jsonb, %s, false)
                        RETURNING episode_id
                        """,
                        (agent_id, tenant_id, kind, json.dumps(content), emb),
                    )
                row = cur.fetchone()
            conn.commit()
        return str(row["episode_id"])

    def recall(self, *, agent_id: str, kind: str | None = None, limit: int = 50) -> list[dict]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                if kind:
                    cur.execute(
                        """
                        SELECT episode_id::text, agent_id, tenant_id, kind, content,
                               embedding::text AS embedding, created_at
                        FROM agent_episodes
                        WHERE agent_id = %s AND kind = %s
                        ORDER BY created_at DESC LIMIT %s
                        """,
                        (agent_id, kind, limit),
                    )
                else:
                    cur.execute(
                        """
                        SELECT episode_id::text, agent_id, tenant_id, kind, content,
                               embedding::text AS embedding, created_at
                        FROM agent_episodes
                        WHERE agent_id = %s
                        ORDER BY created_at DESC LIMIT %s
                        """,
                        (agent_id, limit),
                    )
                rows = cur.fetchall()
        return [dict(r) for r in rows]

    def semantic_search(self, *, agent_id: str, query: str, limit: int = 5) -> list[dict]:
        emb = embed_text(query)
        with self._conn() as conn:
            with conn.cursor() as cur:
                if self._vector_index_ok:
                    # Distributed Vector Indexing path: CRDB VECTOR + <-> distance
                    cur.execute(
                        """
                        SELECT episode_id::text, agent_id, tenant_id, kind, content,
                               embedding::text AS embedding, created_at,
                               (embedding <-> %s::vector) AS distance
                        FROM agent_episodes
                        WHERE agent_id = %s AND embedding IS NOT NULL
                        ORDER BY embedding <-> %s::vector
                        LIMIT %s
                        """,
                        (_vec_literal(emb), agent_id, _vec_literal(emb), limit),
                    )
                    rows = [dict(r) for r in cur.fetchall()]
                    self.last_vector_query = {
                        "mode": "crdb_vector_index_l2_distance",
                        "operator": "<->",
                        "query": query,
                        "hits": len(rows),
                        "claim_distributed_vector_indexing": True,
                        "sql": "ORDER BY embedding <-> $query::vector",
                    }
                    return rows
                # Fallback: pull and rank in Python — NOT claimable as Distributed Vector Indexing
                cur.execute(
                    """
                    SELECT episode_id::text, agent_id, tenant_id, kind, content,
                           embedding, created_at
                    FROM agent_episodes
                    WHERE agent_id = %s AND embedding IS NOT NULL
                    ORDER BY created_at DESC LIMIT 200
                    """,
                    (agent_id,),
                )
                raw = [dict(r) for r in cur.fetchall()]
        scored = []
        for r in raw:
            e = r.get("embedding") or []
            if isinstance(e, (list, tuple)):
                scored.append((cosine(emb, list(e)), r))
        scored.sort(key=lambda x: x[0], reverse=True)
        self.last_vector_query = {
            "mode": "python_cosine_fallback",
            "query": query,
            "hits": len(scored[:limit]),
            "claim_distributed_vector_indexing": False,
        }
        return [r for _, r in scored[:limit]]

    def upsert_task(self, *, agent_id: str, tenant_id: str, goal: str, context: dict) -> str:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO agent_task_state (agent_id, tenant_id, goal, context)
                    VALUES (%s, %s, %s, %s::jsonb)
                    RETURNING task_id
                    """,
                    (agent_id, tenant_id, goal, json.dumps(context)),
                )
                row = cur.fetchone()
            conn.commit()
        return str(row["task_id"])

    def load_policy(self, agent_id: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT agent_id, owner, tenant_id, allowed_effects FROM policy_envelopes WHERE agent_id = %s",
                    (agent_id,),
                )
                row = cur.fetchone()
        return dict(row) if row else None

    def write_receipt(self, receipt: dict[str, Any]) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO fossil_receipts (receipt_id, agent_id, outcome, effect_id, payload)
                    VALUES (%s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (receipt_id) DO NOTHING
                    """,
                    (
                        receipt.get("receipt_id"),
                        receipt.get("agent_id") or "unknown",
                        receipt.get("outcome") or "UNKNOWN",
                        receipt.get("effect_id"),
                        json.dumps(receipt, default=str),
                    ),
                )
            conn.commit()

    def all_receipts(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT receipt_id, agent_id, outcome, effect_id, payload, created_at FROM fossil_receipts ORDER BY created_at"
                )
                rows = cur.fetchall()
        out = []
        for r in rows:
            p = r.get("payload")
            out.append(p if isinstance(p, dict) else dict(r))
        return out

    def record_skill_application(self, *, agent_id: str, skill_evidence: dict[str, Any]) -> str:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO skill_applications (agent_id, skill_id, skill_version, rules_applied)
                    VALUES (%s, %s, %s, %s::jsonb)
                    RETURNING application_id
                    """,
                    (
                        agent_id,
                        skill_evidence.get("skill_id", "unknown"),
                        skill_evidence.get("version", "0"),
                        json.dumps(skill_evidence, default=str),
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return str(row["application_id"])

    def vector_tool_evidence(self) -> dict[str, Any]:
        return {
            "tool": "Distributed Vector Indexing",
            "active": self._vector_index_ok,
            "mode": self.vector_mode,
            "last_query": self.last_vector_query,
            "claimable": bool(
                self._vector_index_ok
                and self.last_vector_query
                and self.last_vector_query.get("claim_distributed_vector_indexing")
            ),
            "schema": "VECTOR(8) + VECTOR INDEX on (agent_id, embedding) + ORDER BY embedding <-> query",
        }


def open_memory_store() -> MemoryStore:
    dsn = os.environ.get("CRDB_DSN") or os.environ.get("DATABASE_URL")
    mode = os.environ.get("HIOP_MEMORY_MODE", "auto").lower()
    if mode == "fixture" or not dsn:
        if mode == "cockroach" and not dsn:
            raise RuntimeError("HIOP_MEMORY_MODE=cockroach but CRDB_DSN unset")
        return InMemoryStore()
    try:
        return CockroachMemoryStore(dsn)
    except Exception as e:
        if mode == "cockroach":
            raise
        store = InMemoryStore()
        store.backend = f"in_memory_fallback:{e}"
        return store
