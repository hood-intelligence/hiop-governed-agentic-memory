# Qualification evidence — HIOP-HACKATHON-FINISH-02

## P0 choice (fastest defensible TWO)

| Tool | Why chosen | Integration point |
|---|---|---|
| **Agent Skills Repo** | Fully local + live; no sponsor account for the skill itself | `skill_loader.py` → orchestrator before authorize |
| **Distributed Vector Indexing** | Named contest feature; SQL VECTOR + INDEX + `<->` | `sql/001_agent_memory.sql` + `CockroachMemoryStore.semantic_search` |

Rejected for RC finish path: Managed MCP (needs live Cloud MCP key + client session); ccloud (CLI install, weaker demo than vector for “memory”).

## Executable proof commands

### Agent Skills (always)

```powershell
$env:HIOP_MEMORY_MODE="fixture"
$env:PYTHONPATH="src"
python -c "from hiop_crdb_adapter.orchestrator import GovernedMemoryAgent; s=GovernedMemoryAgent().run(); print(s['skill_application_id'], s['cockroach_tools'][0])"
python -m pytest tests/test_qualification_tools.py -q
```

Evidence fields in `data/last_run.json` / demo output:
- `skill.participates_in_workflow: true`
- `skill_application_id`
- decisions include `skill_id` / stripped claims

### Distributed Vector Indexing (live CRDB only)

Requires CockroachDB **with VECTOR support** (Cloud current / v25.2+).

```powershell
$env:CRDB_DSN="postgresql://..."
$env:HIOP_MEMORY_MODE="cockroach"
python scripts/01_apply_crdb_schema.py
python scripts/02_run_live_demo.py
# Expect: vector_tool.claimable true, cockroach_tools_claimable_now length 2
```

SQL screenshot:

```sql
SHOW CREATE TABLE agent_episodes;
SELECT kind, embedding FROM agent_episodes WHERE embedding IS NOT NULL LIMIT 3;
```

### AWS Lambda

```powershell
.\scripts\03_build_lambda_zip.ps1
# Upload dist/lambda-hiop-governed-memory.zip; handler.lambda_handler; env CRDB_DSN
```

## Current programmatic status (fixture)

| Gate | Status |
|---|---|
| Agent Skills claimable | YES |
| Distributed Vector Indexing claimable | NO until live CRDB VECTOR |
| AWS Lambda claimable | NO until deploy |
| **SUBMISSION ELIGIBLE** | **NO** |

## Exit condition

`SUBMISSION ELIGIBLE` only when:

1. Live demo prints `cockroach_tools_claimable_now` containing both Agent Skills and Distributed Vector Indexing  
2. Public Lambda URL returns same workflow  
3. Public GitHub + LICENSE  
4. Video  
