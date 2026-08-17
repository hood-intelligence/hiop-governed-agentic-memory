# RC1 submission gate status (execution only)

**Updated:** 2026-08-17  
**Package ZIP SHA:** `934755f1dd43839b5aab637fe3fdf2aa012bea1b88c88fc75e19c9f0d147a2da`  
**Local git commit:** `a893074` — ready to push when remote exists  

| Gate | Status | Blocker |
|---|---|---|
| Fixture tests (15) | **PASS** | — |
| Lambda zip for Console | **READY** | `dist/lambda-hiop-governed-memory.zip` |
| Local git + Apache LICENSE | **READY** | Need public GitHub remote + push |
| Live CockroachDB + VECTOR | **BLOCKED** | Founder: create cluster, set `CRDB_DSN`, or start Docker Desktop |
| Live AWS demo URL | **BLOCKED** | Founder: AWS Console upload zip + Function URL + `CRDB_DSN` env |
| Demo video | **BLOCKED** | After live CRDB |
| Devpost submit | **BLOCKED** | After URLs real |

## Founder actions (copy-paste)

### A. CockroachDB Cloud
1. https://cockroachlabs.cloud → free Serverless  
2. Connection string →  
   `$env:CRDB_DSN = "postgresql://..."`  
3. From package root:  
   `python scripts\01_apply_crdb_schema.py`  
   `python scripts\02_run_live_demo.py`  
4. Must exit 0 with **2 claimable CRDB tools**

### B. AWS Lambda (no CLI)
1. Create function Python 3.12  
2. Upload `dist\lambda-hiop-governed-memory.zip`  
3. Handler: `handler.lambda_handler`  
4. Env: `CRDB_DSN`, `HIOP_MEMORY_MODE=cockroach`  
5. Function URL → demo URL  

### C. GitHub
```powershell
cd "...\HIOP-COCKROACH-AWS-HACKATHON-RC1"
# browser: create PUBLIC empty repo hiop-governed-agentic-memory
git remote add origin https://github.com/YOUR_ORG/hiop-governed-agentic-memory.git
git push -u origin main
```
License URL: `https://github.com/YOUR_ORG/hiop-governed-agentic-memory/blob/main/LICENSE`

### D. Video + Devpost
Follow `docs/DEMO-VIDEO-SCRIPT.md` and `docs/DEVPOST-ANSWERS.md` with real URLs.
