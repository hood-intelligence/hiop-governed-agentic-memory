# Submission eligibility report — HIOP-HACKATHON-FINISH-02

**Date:** 2026-08-16  
**Package:** HIOP-COCKROACH-AWS-HACKATHON-RC1  

## Exit condition status: **NOT SUBMISSION ELIGIBLE** (yet)

| Requirement | Status | Notes |
|---|---|---|
| ≥2 CRDB named tools meaningfully integrated | **PARTIAL** | Skills **YES**; Vector **code YES**, claimable only on live VECTOR-capable CRDB |
| ≥1 AWS service meaningfully integrated | **CODE READY** | Lambda zip/handler ready; not live |
| Functional demo URL | **PENDING** | Founder deploy |
| Public GitHub + LICENSE | **PENDING** | Founder publish |
| Tests | **13 passed** | Includes qualification suite |

## What Grok completed (no overclaim)

### Tool 1 — Agent Skills Repo — **INTEGRATED**
- Runtime load of skill markdown
- `skill_applications` persistence
- Strip memory-authority claims before every authorize
- Policy-before-effect skill gate
- Tests: `tests/test_qualification_tools.py`

### Tool 2 — Distributed Vector Indexing — **INTEGRATED IN CODE**
- Schema: `VECTOR(8)` + `VECTOR INDEX (agent_id, embedding)`
- Live path: `ORDER BY embedding <-> $query::vector`
- Fixture path: **explicitly not claimable**
- Live demo script fails closed if vector not claimable

### AWS Lambda — **INTEGRATED IN CODE**
- `dist/lambda-hiop-governed-memory.zip` / SAM template
- Claim only after Function URL works

## Founder next (only path to SUBMISSION ELIGIBLE)

1. CockroachDB Cloud (current) or Docker image **≥25.2** with VECTOR  
2. `CRDB_DSN` + `python scripts/01_apply_crdb_schema.py` + `02_run_live_demo.py` → must exit 0 with 2 claimable tools  
3. Upload Lambda zip + Function URL  
4. Public GitHub  
5. Video  
6. Fill Devpost from `docs/DEVPOST-ANSWERS.md`  

## Exact form selections when live

- CockroachDB: **Agent Skills Repo** + **Distributed Vector Indexing**  
- AWS: **AWS Lambda**  
- Do not select MCP or ccloud for this entry path  
