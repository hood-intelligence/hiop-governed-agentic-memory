# Acceptance Report — HIOP-COCKROACH-AWS-HACKATHON-RC1

**WO:** `HIOP-GROK-WO-2026-08-16-COCKROACH-AWS-01` · Factory `SPRINT-01-R2`  
**Date:** 2026-08-17  
**Package:** `Hood-Intelligence\03-COMPETITIONS\HIOP-COCKROACH-AWS-HACKATHON-RC1`  
**Handoff ZIP:** `Downloads\HIOP-COCKROACH-AWS-HACKATHON-RC1.zip`  
**Product:** Hood Agent Memory v1 (Developer Agent Platform — Agent Infrastructure)  
**Demo vertical:** Sniper → Terminal-style trail (fixtures only)  

**FEATURE FREEZE:** No further architecture or feature work for this contest. Remaining work is live deploy, public repo, video, Devpost submit only.

---

## VERDICT: **CONDITIONALLY READY** (not yet SUBMISSION ELIGIBLE)

**Last-mile only:** [`docs/READY-TO-SUBMIT-RUNBOOK.md`](docs/READY-TO-SUBMIT-RUNBOOK.md)

| Gate | Result |
|---|---|
| Factory dual-output / rent-to-Hood | PASS — Agent Memory v1 permanent module |
| Open-source firewall (no prod secrets/algorithms) | PASS |
| CockroachDB memory + skill runtime | PASS (code) |
| Distributed Vector Indexing path | PASS (code); **claim only when live VECTOR works** |
| Agent Skills Repo | PASS — claimable offline and live |
| Managed MCP | NOT integrated — **do not claim** |
| AWS Lambda packaging | PASS (code/zip); **claim only when URL live** |
| Sniper vertical (fixture) | PASS — remembered $700 DENY, $650 PERMIT |
| Memory ≠ authority | PASS |
| Fossil receipts | PASS |
| Deterministic fixture demo | PASS |
| **Tests** | **15 passed** |
| Docs / OpenAPI / Devpost drafts | PASS (URLs still placeholders) |
| Live CRDB Cloud (VECTOR-capable) | **FOUNDER** |
| Live AWS demo URL | **FOUNDER** |
| Public GitHub + Apache-2.0 visible | **FOUNDER** |
| ≤3 min video with CRDB memory | **FOUNDER** |
| HoodCar production / prod Supabase | **NOT TOUCHED** |

### Why not READY TO SUBMIT / SUBMISSION ELIGIBLE

External gates only:

1. Live CockroachDB (with VECTOR for second named tool claim)  
2. Live AWS Lambda / Function URL  
3. Public GitHub + license URL  
4. Demo video  

Devpost answers: [`docs/DEVPOST-ANSWERS.md`](docs/DEVPOST-ANSWERS.md) — replace pending URLs when real.

### Claims discipline

| Tool | When to select on form |
|---|---|
| Agent Skills Repo | Yes (integrated now) |
| Distributed Vector Indexing | Only if live demo shows VECTOR INDEX / `<->` path |
| AWS Lambda | Only if public demo URL works |
| Managed MCP / S3 | Do not select unless live |

---

## Demo proof (fixture) — independently re-runnable

```text
pytest: 15 passed

Lab / telemetry path: PERMIT
Maneuver + memory claims: DENY
Sniper: remembered $700 offer → DENY
Sniper: $650 within policy max $675 → PERMIT
Receipts + skill application recorded
```

```powershell
$env:HIOP_MEMORY_MODE = "fixture"
$env:PYTHONPATH = "src"
python -m pytest tests -q
python demo\run_sniper_demo.py
```

---

## Founder path (feature freeze — ops only)

1. CockroachDB Cloud (VECTOR-capable) → `CRDB_DSN`  
2. `python scripts\01_apply_crdb_schema.py` + `python scripts\02_run_live_demo.py` (must show 2 claimable CRDB tools)  
3. Upload `dist\lambda-hiop-governed-memory.zip` or SAM → Function URL  
4. Public GitHub (module + fixtures only; Apache-2.0)  
5. Record ≤3 min video (CRDB SQL + Sniper DENY/PERMIT)  
6. Fill real URLs on Devpost → **Submit by Aug 18 5:00 PM EDT**  

---

## SHA

Verify against current Downloads handoff:

- RC1 ZIP: see `HIOP-COCKROACH-AWS-HACKATHON-RC1.SHA256.txt`  
- Factory ZIP: see `HOOD-HACKATHON-FACTORY-2026-08-16.SHA256.txt`  

(Last founder-verified RC1 content hash in session: `024cf3ca763510cedfed101ca90f751ac240a33abf2e15950ac427761132b4d4` — re-hash after this doc-only fix if re-zipping.)
