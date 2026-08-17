# READY TO SUBMIT runbook  
## CONDITIONALLY READY → READY TO SUBMIT

**No new features.** Use this exact RC1 package.  
**Project name:** `HIOP Governed Agentic Memory`  
**Tagline:** `CockroachDB remembers. HIOP decides. Memory never becomes authority.`  
**Built with (until deploy):** `CockroachDB`, `Python`, `HIOP Effect Authority`  
**Add after live:** `AWS Lambda` only when API works. **S3** only if receipt bucket used.  
**Never claim:** Distributed Vector Indexing · Managed MCP Server  

**Deadline:** 2026-08-18 5:00 PM EDT  

---

## Gate 0 — Tooling (once per machine)

| Tool | Why | Action if missing |
|---|---|---|
| Docker Desktop | Optional local CRDB | Start app from Start Menu |
| Python 3.12 | Demo / tests | Already present |
| git | GitHub publish | Already present |
| AWS account + **AWS CLI** | Lambda deploy | https://aws.amazon.com/cli/ or `winget install Amazon.AWSCLI` |
| **SAM CLI** (optional) | Guided deploy | Or use Console zip upload (Gate 2B) |
| GitHub account | Public repo | Create repo in browser |
| CockroachDB Cloud | Live memory | https://cockroachlabs.cloud/signup |

Check from package root:

```powershell
.\scripts\00_check_prereqs.ps1
```

---

## Gate 1 — Live CockroachDB Cloud (do first)

### 1.1 Create cluster

1. https://cockroachlabs.cloud/signup  
2. Create free **Serverless** cluster  
3. Create SQL user + password  
4. Network: allow your IP (or `0.0.0.0/0` for demo only — understand risk)  
5. Copy **connection string** → keep password private  

### 1.2 Apply schema + live demo

```powershell
cd "...\HIOP-COCKROACH-AWS-HACKATHON-RC1"
pip install -r requirements.txt
$env:CRDB_DSN = "postgresql://USER:PASSWORD@HOST:26257/defaultdb?sslmode=verify-full"
python scripts\01_apply_crdb_schema.py
python scripts\02_run_live_demo.py
```

**Pass criteria:**

- Script prints `memory_backend: cockroachdb` (not fixture)  
- SQL shell shows rows:

```sql
SELECT kind, created_at FROM agent_episodes ORDER BY created_at DESC LIMIT 10;
SELECT outcome, effect_id FROM fossil_receipts ORDER BY created_at DESC LIMIT 10;
```

- Demo shows PERMIT lab, DENY maneuver (memory claim), DENY rename/wire, PERMIT after human  

**Screenshot for video:** Cloud SQL results + terminal deny line.

---

## Gate 2 — Live AWS demo URL

### Option A — SAM (if CLI installed)

```powershell
aws configure   # once
sam build -t deploy\aws\template.yaml
sam deploy --guided `
  --parameter-overrides "CrdbDsn=$env:CRDB_DSN" `
  --capabilities CAPABILITY_IAM
```

Copy **ApiUrl** output. Test:

```powershell
curl -X POST "https://XXXX.execute-api.REGION.amazonaws.com/Prod/run" `
  -H "Content-Type: application/json" `
  -d "{\"goal\":\"lab safe\"}"
```

### Option B — Console zip (no SAM) **recommended if tools missing**

```powershell
.\scripts\03_build_lambda_zip.ps1
# produces: dist\lambda-hiop-governed-memory.zip
```

Then AWS Console:

1. Lambda → Create function → Python 3.12 → name `hiop-governed-agentic-memory`  
2. Upload `dist\lambda-hiop-governed-memory.zip`  
3. Handler: `handler.lambda_handler`  
4. Config → Environment variables:  
   - `CRDB_DSN` = (same as Gate 1)  
   - `HIOP_MEMORY_MODE` = `cockroach`  
   - `HIOP_PRODUCTION_CERTIFIED` = `false`  
   - **Do not set** `S3_RECEIPT_BUCKET` unless you create a bucket (then you may claim S3)  
5. Timeout 60s, memory 512 MB  
6. Configuration → Function URL → Create → Auth **NONE** for public demo (staging only)  
   **or** API Gateway HTTP API → POST `/run`  

**Pass criteria:** Public URL returns JSON with `results` and permit/deny outcomes.

**Built with on Devpost:** add `AWS Lambda` only after this works.

---

## Gate 3 — Public GitHub (Apache-2.0)

```powershell
.\scripts\04_prepare_git_repo.ps1
```

Then in browser: github.com/new → public repo name e.g. `hiop-governed-agentic-memory`  
**Do not** initialize with README (we have one).

```powershell
cd "...\HIOP-COCKROACH-AWS-HACKATHON-RC1"
git remote add origin https://github.com/YOUR_ORG/hiop-governed-agentic-memory.git
git push -u origin main
```

**Pass criteria:**

- Repo **public**  
- `LICENSE` Apache-2.0 visible on main page  
- `docs/PREEXISTING-DISCLOSURE.md` present  
- README tagline matches package  

---

## Gate 4 — Video ≤ 3 minutes

Follow `docs/DEMO-VIDEO-SCRIPT.md`. **Must show:**

1. CockroachDB SQL / Console with `agent_episodes` or `fossil_receipts`  
2. Terminal or Lambda response: PERMIT lab  
3. DENY maneuver despite remembered credential  
4. Human approval → PERMIT  
5. One sentence: Memory never becomes authority  

Upload YouTube or Vimeo **public**.

---

## Gate 5 — Devpost form (final)

| Field | Value |
|---|---|
| Project name | HIOP Governed Agentic Memory |
| Tagline | CockroachDB remembers. HIOP decides. Memory never becomes authority. |
| Built with | CockroachDB, Python, HIOP Effect Authority, **AWS Lambda** (if live) |
| CRDB tools | **Agent Skills** + **ccloud/Cloud** (after Gate 1). Not VECTOR INDEX. Not MCP. |
| AWS | **Lambda** (if live). S3 only if used. |
| Repo URL | public GitHub |
| Demo URL | Function URL / API Gateway |
| Video | YouTube/Vimeo link |
| Description | paste from `docs/DEVPOST-COPY.md` |

Check Official Rules box → **Submit**.

---

## READY TO SUBMIT scorecard

| # | Item | Owner | Done? |
|---|---|---|---|
| 1 | Live CRDB + schema + demo `cockroachdb` backend | Founder | ☐ |
| 2 | Public demo URL on AWS Lambda | Founder | ☐ |
| 3 | Public GitHub + Apache-2.0 | Founder | ☐ |
| 4 | ≤3 min video with CRDB + deny sequence | Founder | ☐ |
| 5 | Devpost submit before Aug 18 5 PM EDT | Founder | ☐ |

When all five are ☑ → verdict becomes **READY TO SUBMIT**.

Grok can re-run `scripts/05_readiness_check.ps1` after you set `CRDB_DSN` and `DEMO_URL` env vars to verify 1–2 programmatically.
