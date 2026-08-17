# Exact Devpost field answers (update URLs when live)

## Project name
HIOP Governed Agentic Memory

## Tagline
CockroachDB remembers. HIOP decides. Memory never becomes authority.

## Functional demo URL
`pending deployment`  
*(set after Lambda Function URL works — then paste URL here and on form)*

## Testing instructions
No credentials required. Open the demo and run the governed-memory scenario. The demonstration stores agent memory in CockroachDB, recalls prior context via distributed vector search, independently evaluates effect authority, denies unauthorized reuse of remembered authority, records human approval, and preserves the resulting decision/evidence trail.

## Public repository
`pending GitHub publication`

## License URL
`https://github.com/<ORG>/hiop-governed-agentic-memory/blob/main/LICENSE`  
*(Apache-2.0 file in repo root)*

## CockroachDB tools used (select ONLY when claimable)

**When live vector CRDB is proven, select exactly:**

1. **Agent Skills Repo**  
2. **Distributed Vector Indexing**

**Do NOT select:** Managed MCP Server, ccloud CLI (unless separately integrated later).

### Meaningful integration explanation

> **Agent Skills Repo:** At runtime the agent loads `skills/hiop-governed-memory/SKILL.md`, records `skill_applications`, and enforces skill rules before every effect—including stripping memory-derived “I am authorized” claims and requiring `policy_envelopes` before mediation.  
>  
> **Distributed Vector Indexing:** Episodes persist `VECTOR(8)` embeddings under a CockroachDB `VECTOR INDEX`. The agent’s semantic recall of credentials/plans uses `ORDER BY embedding <-> query::vector` so vector search is part of the live workflow before HIOP permit/deny.  
>  
> **HIOP:** Separates memory from authority so recall never expands what the agent may cause.

## AWS services used
Select **AWS Lambda** only after deploy is live.  
Do not select S3 unless receipt bucket is configured and used.

## Start date
`2026-08-16` *(actual start of this hackathon-specific package — do not backdate)*

## Submitter type
Organization

## Country
United States

## Organization
Hood Intelligence Corporation

## Learning
Significant

## AI career value
Yes

## Pre-existing work disclosure
HIOP Governed Agent Memory was created during the hackathon submission period. The project incorporates pre-existing HIOP architectural concepts and governance research developed by Hood Intelligence Corporation. The hackathon-specific implementation, CockroachDB integration, AWS integration, agent-memory workflow, demonstration scenario, deployment configuration, testing, and submission materials were created for this project during the submission period. Pre-existing HIOP materials are disclosed and are not represented as work created during the hackathon.

## AI tools leveraged
Grok (xAI)

## Built with
CockroachDB, Python, HIOP Effect Authority  
*(add AWS Lambda only after live)*
