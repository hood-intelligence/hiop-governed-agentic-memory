# Demo video script (≤ 3 minutes)

**Must show CockroachDB memory at work.**

## 0:00–0:25 Problem

> Agents need memory that never dies.  
> But if memory becomes permission, agents become dangerous.  
> **HIOP: CockroachDB remembers. Authority decides separately.**

## 0:25–0:50 Architecture (10s diagram)

Show `docs/ARCHITECTURE.md` / mermaid.  
Call out: Lambda + CRDB + HIOP.  
**Do not say “Distributed Vector Indexing”** unless we upgraded to CRDB VECTOR index. Say “durable embeddings in CockroachDB, semantic recall in the agent.”

## 0:50–1:40 Live demo

1. `docker compose` CRDB or Cloud console  
2. `python demo/run_demo.py` with `HIOP_MEMORY_MODE=cockroach`  
3. Show SQL:

```sql
SELECT kind, content FROM agent_episodes ORDER BY created_at DESC LIMIT 5;
```

4. Point at `credential_seen` row  
5. Show terminal: maneuver **DENY** despite memory  
6. Lab **PERMIT** + receipt  

## 1:40–2:20 AWS

Show Lambda console or API POST `/run` response JSON.  
Optional S3 object with receipt.

## 2:20–2:50 Close

> Memory ≠ authority.  
> Hood Intelligence — HIOP Governed Agentic Memory on CockroachDB and AWS.

## Shot list

- [ ] CRDB SQL / Console  
- [ ] Terminal permit/deny  
- [ ] Architecture slide  
- [ ] Lambda or API response  
