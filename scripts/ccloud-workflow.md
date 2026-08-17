# ccloud / Cloud workflow (second claimed CRDB tool — when you actually run it)

Do this after signup at https://cockroachlabs.cloud/

## Option A — Cloud Console (minimum)

1. Create free **Serverless** cluster (region near you).
2. Create SQL user + password; allow your IP / `0.0.0.0/0` for demo only if you accept risk.
3. Copy connection string → `CRDB_DSN` env var  
   Example shape: `postgresql://user:pass@host:26257/defaultdb?sslmode=verify-full`
4. Open **SQL shell** in console and paste contents of `sql/001_agent_memory.sql`.
5. Run demo:

```powershell
$env:CRDB_DSN = "<paste>"
$env:HIOP_MEMORY_MODE = "cockroach"
$env:PYTHONPATH = "src"
python demo\run_demo.py
```

6. In SQL shell prove memory:

```sql
SELECT kind, left(content::string, 80) FROM agent_episodes ORDER BY created_at DESC LIMIT 10;
SELECT * FROM fossil_receipts ORDER BY created_at DESC LIMIT 5;
```

## Option B — ccloud CLI (preferred for “ccloud CLI” claim)

```text
# install: https://www.cockroachlabs.com/docs/cockroachcloud/ccloud-get-started
ccloud auth login
ccloud cluster list
ccloud cluster sql <cluster-name> --user root
# then \i or paste 001_agent_memory.sql
```

Screenshot for video: cluster list + SQL select on `agent_episodes`.

## Do not claim until steps above are real

If you never create a cluster, claim only **Agent Skills** in docs and leave second tool blank until live — package stays CONDITIONALLY READY.
