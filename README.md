# HIOP Governed Agentic Memory

**CockroachDB remembers. HIOP decides. Memory never becomes authority.**

Apache-2.0 public demonstrator for the CockroachDB × AWS agentic-memory hackathon.

## Maturity

HIOP Effect Authority is a live-development-validated governed-agent runtime demonstrating durable CockroachDB persistence, tenant isolation, idempotent effects, tamper-resistant evidence receipts, receipt-chain verification, and fail-closed behavior. It is a development demonstrator and is not represented as a production-certified deployment.

This repository is the **submission-safe** demonstrator. It does **not** contain Hood production systems, production credentials, HoodCar, or the proprietary HIOP runtime tree.

## What this is

An agent stores and retrieves memory in CockroachDB (episodes, embeddings, task state, receipts). Before any effect, a local HIOP-style gateway evaluates a **policy envelope**. Remembered credentials or prior actions never expand authority.

| Layer | Implementation |
|---|---|
| Persistent memory | CockroachDB (`agent_episodes`, VECTOR embeddings, `agent_task_state`, `fossil_receipts`) |
| Qualifying tools | **Agent Skills Repo** (runtime) + **Distributed Vector Indexing** (claim Vector only when live CRDB VECTOR is proven) |
| AWS | **AWS Lambda** (claim only after a public Function URL works) |
| Authority | In-repo gateway (`src/hiop_crdb_adapter/gateway.py`) — not the closed HIOP product tree |

Do **not** claim Managed MCP Server or ccloud unless you actually used them.

## Quick start (offline)

```powershell
pip install -r requirements.txt
$env:HIOP_MEMORY_MODE = "fixture"
$env:PYTHONPATH = "src"
python demo\run_demo.py
python demo\run_sniper_demo.py
python -m pytest tests -q
```

Expect 15 tests passed. Sniper fixture: remembered $700 offer **DENY**; $650 **PERMIT**.

## Live CockroachDB

```powershell
# Docker
cd deploy\docker
docker compose up -d
$env:CRDB_DSN = "postgresql://root@localhost:26257/defaultdb?sslmode=disable"
$env:HIOP_MEMORY_MODE = "cockroach"
$env:PYTHONPATH = "..\..\src"
python ..\..\scripts\01_apply_crdb_schema.py
python ..\..\demo\run_demo.py
```

Or set `CRDB_DSN` to a CockroachDB Cloud URL (do not commit it).

## AWS Lambda

```powershell
.\scripts\03_build_lambda_zip.ps1
```

Upload `dist\lambda-hiop-governed-memory.zip` → Python 3.12 → handler `handler.lambda_handler` → env `CRDB_DSN`, `HIOP_MEMORY_MODE=cockroach` → Function URL.

## Invariant

Memory ≠ authority. Recall never grants effects.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
