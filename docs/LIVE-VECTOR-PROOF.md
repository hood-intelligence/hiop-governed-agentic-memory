# Live VECTOR proof — hiop_agent_memory

**Decision: PASS**

`hiop_dev` was not written. Database used: **hiop_agent_memory**.

| Item | Result |
|---|---|
| Cockroach CLI | v25.3.0 |
| CREATE DATABASE | OK via defaultdb |
| Schema | `scripts/01_apply_crdb_schema.py` OK |
| Vector column | `embedding` type `VECTOR(8)` |
| Vector index | `VECTOR INDEX idx_agent_episodes_embedding (agent_id, embedding vector_l2_ops)` |
| Live `<->` | 1 hit, distance 0.0, kind `credential_seen` |
| memory_backend | **cockroachdb** |
| Claimable tools | Agent Skills Repo, Distributed Vector Indexing |
| claimable count | **2** |
| Official demo | PERMIT lab, DENY first maneuver, 2 tools claimable |
| Tests | 18 passed (plus 2 new guard tests) |
| production_certified | false |

Rotate the admin password that was pasted into chat.
