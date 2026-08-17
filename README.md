# HIOP Governed Agentic Memory  
## CockroachDB × AWS Hackathon RC1  
### Hood Hackathon Factory · sprint-0 of **Hood Governed Memory Fabric**

**Factory:** [`../HOOD-HACKATHON-FACTORY/`](../HOOD-HACKATHON-FACTORY/)  
**Work orders:** `HIOP-GROK-WO-2026-08-16-COCKROACH-AWS-01` · `HOOD-HACKATHON-FACTORY-SPRINT-01`  
**Entrant:** Hood Intelligence Corporation  
**Deadline:** 2026-08-18 5:00 PM EDT  
**Prize pool:** $8,750 (optional upside — **platform capability is the default win**)  

### Dual output

| Contest | Hood (permanent) |
|---|---|
| Judgeable agentic memory on CRDB + AWS | **Hood Agent Memory v1** on **Developer Agent Platform** |
| Sniper opportunity demo (fixtures) | Sniper/Terminal vertical pattern; **no production access** |

```
DATA + INTELLIGENCE (existing Hood Developer) 
        → AGENT INFRASTRUCTURE (this package: memory/authority/receipts)
        → APPLICATIONS (Sniper demo vertical → later Terminal)
```

### Sniper demo (fixtures only)

```powershell
$env:HIOP_MEMORY_MODE="fixture"
$env:PYTHONPATH="src"
python demo\run_sniper_demo.py
```

Expect: remembered $700 offer **DENY**; $650 within policy **PERMIT**; Terminal-style JSON trail.

### One line

> **CockroachDB remembers. HIOP decides. Memory never becomes authority.**

### Invariant

> Memory != authority. An agent remembering credentials, routes, prior actions, or capabilities must **not** automatically increase what it is authorized to cause.

---

## Architecture

```
Goal → Agent plan
     → CockroachDB persistent memory (episodes + embeddings + task state)
     → HIOP Effect Authority (policy envelopes)
     → PERMIT → simulated execute → Fossil receipts (CRDB + optional S3)
     → DENY   → fossilize denial (memory of denial ≠ future permit)
```

| Layer | Technology |
|---|---|
| Persistent agent memory | **CockroachDB** (`agent_episodes`, `FLOAT8[]` embeddings, `agent_task_state`, receipts) |
| CRDB tools (qualification) | **Agent Skills** (runtime) + **Distributed Vector Indexing** (`VECTOR` + index + `<->`) — claim Vector only when live CRDB proves it |
| CRDB tools **not** claimed | Managed MCP; ccloud CLI (not this path) |
| AWS (≥1 required) | **AWS Lambda** runtime + optional **S3** receipt mirror |
| Authority | HIOP gateway (P1 Effect Authority pattern — not redesigned) |

---

## Quick start (offline fixture — tests judges can run immediately)

```powershell
cd "C:\Users\glitt\OneDrive\Desktop\Hood-Intelligence\03-COMPETITIONS\HIOP-COCKROACH-AWS-HACKATHON-RC1"
pip install -r requirements.txt
$env:HIOP_MEMORY_MODE = "fixture"
$env:PYTHONPATH = "src"
python demo\run_demo.py
python -m pytest tests -q
```

## Local CockroachDB (genuine memory backend)

```powershell
cd deploy\docker
docker compose up -d
# wait healthy, then:
$env:CRDB_DSN = "postgresql://root@localhost:26257/defaultdb?sslmode=disable"
$env:HIOP_MEMORY_MODE = "cockroach"
$env:PYTHONPATH = "..\..\src"
python ..\..\demo\run_demo.py
```

## AWS deploy (functional demo URL)

```powershell
# Requires AWS SAM CLI + credentials + CRDB Cloud DSN
sam build -t deploy\aws\template.yaml
sam deploy --guided --parameter-overrides CrdbDsn="postgresql://..."
# POST https://{api}.amazonaws.com/Prod/run  {"goal":"..."}
```

See [`docs/SETUP.md`](docs/SETUP.md).

---

## Demo scenario (one excellent path)

1. Agent stores goal + plan in CRDB  
2. Discovers tools; **remembers** a maneuver credential in memory  
3. Semantic recall finds credential episode (vector memory)  
4. `telemetry.analyze` → **PERMIT**  
5. `lab.adjust_setpoint` → **PERMIT** + fire  
6. `spacecraft.maneuver` with memory claim → **DENY**  
7. Rename `orbit_nudge` → **DENY**  
8. `payments.wire` from remembered route → **DENY**  
9. Human elevates maneuver → **PERMIT** + fire  
10. Fossil receipts durable  

---

## Pre-existing disclosure

HIOP Effect Authority core (P1 RC1/RC2) is disclosed pre-existing product.  
**Built for this contest:** CRDB memory schema, vector episodes, skills, MCP binding, Lambda/S3 adapter, mission demo, tests, Devpost package.

See [`docs/PREEXISTING-DISCLOSURE.md`](docs/PREEXISTING-DISCLOSURE.md).

---

## Docs

| File | Purpose |
|---|---|
| **[`docs/READY-TO-SUBMIT-RUNBOOK.md`](docs/READY-TO-SUBMIT-RUNBOOK.md)** | **CONDITIONALLY READY → SUBMIT (start here)** |
| [`docs/CLAIMS-TRUTH.md`](docs/CLAIMS-TRUTH.md) | What to claim on Devpost |
| [`docs/COMPLIANCE-CHECKLIST.md`](docs/COMPLIANCE-CHECKLIST.md) | Rules → evidence |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Diagram |
| [`docs/DEVPOST-COPY.md`](docs/DEVPOST-COPY.md) | Submission text |
| [`docs/DEMO-VIDEO-SCRIPT.md`](docs/DEMO-VIDEO-SCRIPT.md) | ≤3 min script |
| [`docs/SETUP.md`](docs/SETUP.md) | Spin-up |
| [`ACCEPTANCE-REPORT.md`](ACCEPTANCE-REPORT.md) | Verdict + hashes |

### Last-mile scripts (no new product features)

```powershell
.\scripts\00_check_prereqs.ps1
# after Cloud DSN:
python scripts\01_apply_crdb_schema.py
python scripts\02_run_live_demo.py
.\scripts\03_build_lambda_zip.ps1    # Console upload zip
.\scripts\04_prepare_git_repo.ps1
.\scripts\05_readiness_check.ps1
```

## License

Apache-2.0 — see [`LICENSE`](LICENSE) (required for public Devpost repo).

## Constraints honored

- No HoodCar production changes  
- No patent changes  
- No HIOP architectural redesign  
- Work under `Hood-Intelligence` only  
