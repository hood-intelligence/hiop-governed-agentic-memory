"""Live VECTOR proof against hiop_agent_memory only. Never prints DSN. Never touches hiop_dev."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SQL = ROOT / "sql" / "001_agent_memory.sql"
EVID = ROOT / "data" / "LIVE-VECTOR-PROOF.json"


def _dsn() -> str:
    dsn = os.environ.get("CRDB_DSN") or os.environ.get("HIOP_CRDB_DSN") or os.environ.get("DATABASE_URL") or ""
    if not dsn:
        u = os.environ.get("USERPROFILE", "")
        # process-only; user env is injected by caller
    return dsn.strip()


def _db_name(dsn: str) -> str:
    path = (urlparse(dsn).path or "").lstrip("/")
    return path.split("?")[0]


def main() -> int:
    dsn = _dsn()
    if not dsn:
        print("BLOCKED: CRDB_DSN not set")
        return 1
    db = _db_name(dsn)
    if db == "hiop_dev":
        print("BLOCKED: DSN targets hiop_dev — frozen. Rewrite to hiop_agent_memory first.")
        return 3
    if db != "hiop_agent_memory":
        print(f"BLOCKED: current DSN database is {db!r}, expected hiop_agent_memory")
        return 3

    import psycopg

    evidence: dict = {"database": db, "steps": []}
    with psycopg.connect(dsn) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            cur_db = cur.fetchone()[0]
            evidence["current_database"] = cur_db
            print("current_database=" + str(cur_db))
            if str(cur_db) == "hiop_dev":
                print("BLOCKED: connected to hiop_dev")
                return 3
            if str(cur_db) != "hiop_agent_memory":
                print("BLOCKED: unexpected database " + str(cur_db))
                return 3

            cur.execute(SQL.read_text(encoding="utf-8"))
            evidence["steps"].append("schema_applied")
            print("schema_applied=OK")

            cur.execute(
                """
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name='agent_episodes' AND column_name='embedding'
                """
            )
            emb = cur.fetchone()
            evidence["embedding_column"] = list(emb) if emb else None
            print("embedding_column=" + json.dumps(evidence["embedding_column"]))
            if not emb or "vector" not in str(emb).lower():
                print("BLOCKED: embedding is not VECTOR")
                return 4

            cur.execute("SHOW CREATE TABLE agent_episodes")
            create = cur.fetchone()
            ddl = create[-1] if create else ""
            evidence["show_create"] = ddl
            print("show_create_has_VECTOR8=" + str("VECTOR(8)" in ddl.upper().replace(" ", "")))
            print("show_create_has_VECTOR_INDEX=" + str("VECTOR INDEX" in ddl.upper()))
            vec_ok = "VECTOR INDEX" in ddl.upper() and "VECTOR" in ddl.upper()
            if not vec_ok:
                print("BLOCKED: VECTOR INDEX not present")
                return 4

            # live <-> query
            cur.execute(
                """
                INSERT INTO agent_episodes (agent_id, tenant_id, kind, content, embedding)
                VALUES ('ops-memory-agent', 'tenant-mission', 'credential_seen',
                        '{"source":"live-vector-proof"}'::jsonb,
                        '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]'::vector)
                """
            )
            cur.execute(
                """
                SELECT kind, (embedding <-> '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]'::vector) AS distance
                FROM agent_episodes
                WHERE agent_id = 'ops-memory-agent' AND embedding IS NOT NULL
                ORDER BY embedding <-> '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]'::vector
                LIMIT 3
                """
            )
            hits = cur.fetchall()
            evidence["vector_query_hits"] = [{"kind": h[0], "distance": float(h[1])} for h in hits]
            print("vector_query_hits=" + json.dumps(evidence["vector_query_hits"]))
            if not hits:
                print("BLOCKED: <-> returned no rows")
                return 5

    os.environ["HIOP_MEMORY_MODE"] = "cockroach"
    os.environ["CRDB_DSN"] = dsn
    from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent

    summary = GovernedMemoryAgent().run()
    backend = summary.get("memory_backend")
    claimable = summary.get("cockroach_tools_claimable_now") or []
    vector = summary.get("vector_tool") or {}
    evidence["memory_backend"] = backend
    evidence["claimable"] = claimable
    evidence["vector_tool_claimable"] = bool(vector.get("claimable"))
    evidence["production_certified"] = summary.get("production_certified")
    print("memory_backend=" + str(backend))
    print("claimable=" + json.dumps(claimable))
    print("vector_claimable=" + str(evidence["vector_tool_claimable"]))
    EVID.parent.mkdir(parents=True, exist_ok=True)
    EVID.write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")
    print("wrote data/LIVE-VECTOR-PROOF.json")
    if not str(backend).startswith("cockroach"):
        print("BLOCKED: backend not cockroachdb")
        return 6
    if len(claimable) < 2 or not evidence["vector_tool_claimable"]:
        print("BLOCKED: need 2 claimable tools including Distributed Vector Indexing")
        return 7
    print("PASS live vector proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
