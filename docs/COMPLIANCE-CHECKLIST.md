# Compliance Checklist — CockroachDB × AWS Hackathon

**Rules:** https://cockroachdb-ai.devpost.com/rules  
**Deadline:** 2026-08-18 5:00 PM EDT  
**Claims policy:** [`CLAIMS-TRUTH.md`](CLAIMS-TRUTH.md)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Agentic app | MET | `src/hiop_crdb_adapter/orchestrator.py` |
| 2 | CockroachDB as **persistent memory layer** | MET (code) / FOUNDER (live cluster) | `sql/001_agent_memory.sql`, `memory_store.py`, docker-compose |
| 3 | Meaningfully integrated (not just initialized) | MET | episodes, embeddings, tasks, receipts, policy tables |
| 4 | ≥2 CRDB **named** tools | **PARTIAL until live** | See 4a–4d — claim only what is true |
| 4a | Distributed Vector Indexing | **DO NOT CLAIM** | FLOAT8[] + app-side cosine only — not CRDB VECTOR index product |
| 4b | Agent Skills Repo | **MET — claim** | `skills/hiop-governed-memory/SKILL.md` |
| 4c | Managed MCP Server | **DO NOT CLAIM** | Example config only — not live |
| 4d | ccloud CLI / Cloud control plane | **FOUNDER — claim after use** | `scripts/ccloud-workflow.md` |
| 5 | ≥1 AWS service | MET (code) / FOUNDER (deploy) | Lambda `deploy/aws/handler.py` + optional S3 |
| 6 | Public OSS repo + Apache/MIT | FOUNDER-ACTION | `LICENSE` Apache-2.0 |
| 7 | Functional demo URL | FOUNDER-ACTION | SAM API URL |
| 8 | Text description | MET | `docs/DEVPOST-COPY.md` |
| 9 | Video ≤3 min with CRDB memory | FOUNDER-ACTION | `docs/DEMO-VIDEO-SCRIPT.md` |
| 10 | Identify CRDB tools used + how | MET (honest copy) | CLAIMS-TRUTH + DEVPOST-COPY |
| 11 | Identify AWS services used + how | MET | DEVPOST-COPY |
| 12 | Architecture diagram | MET | `docs/ARCHITECTURE.md` |
| 13 | New project + disclose pre-existing | MET | `docs/PREEXISTING-DISCLOSURE.md` |

## Judging criteria map

| Criterion | How we score (honest) |
|---|---|
| Agentic Memory Design | CRDB stores plans, discoveries, credentials, denials, embeddings, task state |
| Technological Implementation | Schema + skills + Lambda; no fake VECTOR INDEX / MCP |
| Real-World Impact | Agents that remember without becoming unsafe |
| Product Readiness | Fail-closed, receipts, separate policy table |
| Creativity | **Memory ≠ authority** |

## Founder must complete before submit

1. Join Devpost (done or in progress)  
2. CockroachDB Cloud free cluster → `CRDB_DSN` + apply SQL  
3. Run demo with `HIOP_MEMORY_MODE=cockroach`  
4. AWS SAM deploy Lambda → demo URL  
5. Public GitHub Apache-2.0  
6. Video: SQL memory + HIOP DENY after credential memory  
7. Form: claim **Skills + ccloud/Cloud**; **not** VECTOR INDEX or MCP  
