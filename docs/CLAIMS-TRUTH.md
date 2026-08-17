# Claims truth — post QUALIFICATION GATE (FINISH-02)

## Selected CockroachDB tools (target for form)

| # | Named tool | Integration | When claimable |
|---|---|---|---|
| 1 | **Agent Skills Repo** | Runtime load of `skills/hiop-governed-memory/SKILL.md`; `skill_applications` row; strips memory-authority claims before every authorize | **Always** (fixture + live) |
| 2 | **Distributed Vector Indexing** | `VECTOR(8)` column, `VECTOR INDEX (agent_id, embedding)`, `semantic_search` uses `ORDER BY embedding <-> query::vector` | **Only when** live CRDB applies vector schema and `vector_tool.claimable=true` |
| — | Managed MCP Server | Not integrated | **Do not claim** |
| — | ccloud CLI | Not required for this path | Optional later |

## AWS

| Service | When claimable |
|---|---|
| **AWS Lambda** | After public Function URL / API works with live handler |
| S3 | Only if `S3_RECEIPT_BUCKET` used |

## Eligibility equation

```
SUBMISSION ELIGIBLE ⇔
  Agent Skills claimable
  AND Distributed Vector Indexing claimable (live CRDB with VECTOR)
  AND AWS Lambda live demo URL
  AND public GitHub + LICENSE
  AND video
```

On fixture-only runs: Skills=1, Vector=0 → **NOT ELIGIBLE** (expected).  
After Cloud/docker CRDB 25.2+ with vector: Skills+Vector=2 → CRDB gate pass.

## Devpost “how” blurbs (paste when live)

**Agent Skills Repo**

> The agent loads `hiop-governed-memory` from the Agent Skills tree at run start, writes a `skill_applications` audit row, and enforces skill rules on every effect: policy must load from `policy_envelopes`; claims like `force_permit` / `remembered_credential` are stripped before HIOP mediation so remembered credentials cannot expand authority.

**Distributed Vector Indexing**

> Agent episodes store `embedding VECTOR(8)` with a CockroachDB `VECTOR INDEX` on `(agent_id, embedding)`. Semantic recall of prior credentials/plans uses SQL `ORDER BY embedding <-> $query::vector`, so vector search participates in the remember→reason path before authorize/deny.
