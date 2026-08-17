# Architecture

```mermaid
flowchart LR
  U[Operator / API] --> L[AWS Lambda]
  L --> A[Governed Memory Agent]
  A --> M[(CockroachDB Memory)]
  A --> P[(policy_envelopes)]
  A --> H[HIOP Gateway]
  H -->|PERMIT| E[Simulated Effector]
  H -->|DENY| F[Fossil Receipts]
  E --> F
  F --> M
  F --> S3[(S3 optional)]
  A --> V[App-side semantic recall on FLOAT8 embeddings]
  V --> M
  SK[Agent Skills] -.-> A
  CC[ccloud / Cloud SQL] -.-> M
```

Note: Managed MCP and CRDB VECTOR INDEX are **not** in the live RC1 path.

## Data plane vs control plane

| Plane | Store | May do | Must not do |
|---|---|---|---|
| Memory (CRDB) | episodes, embeddings, tasks | recall context | grant effects |
| Policy (CRDB policy_envelopes) | allowed_effects | define envelope | be written by agent self |
| Authority (HIOP) | decisions | PERMIT/DENY | skip mediation |
| Evidence (fossil_receipts + S3) | receipts | audit/replay | alter past |

## Why this fits the hackathon theme

Agentic systems fail when memory is offline **or** when memory is confused with permission.  
We use CockroachDB for always-on memory and HIOP so **remembered capability never equals authorized effect**.
