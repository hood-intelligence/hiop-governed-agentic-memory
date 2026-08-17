# Devpost submission copy

## Project name

**HIOP Governed Agentic Memory**

## Tagline

CockroachDB remembers. HIOP decides. Memory never becomes authority.

## Description

AI agents need durable memory — plans, context, discoveries, even credentials they once saw. Production systems also need a hard line: **remembering how to do something must not mean being allowed to do it.**

**HIOP Governed Agentic Memory** is an agentic application that uses **CockroachDB as its persistent memory layer** and runs on **AWS Lambda**, with **HIOP Effect Authority** mediating every real-world effect.

### How it works

1. The agent receives a mission goal and stores plan + task state in **CockroachDB**.  
2. Episodes may include `FLOAT8[]` embeddings; the agent performs **application-side semantic recall** over that durable memory (we do **not** claim the named “Distributed Vector Indexing” product feature in RC1).  
3. The agent discovers tools and even **stores a remembered credential** for a spacecraft maneuver.  
4. Semantic recall retrieves that memory.  
5. Analysis and in-envelope lab adjustments are **PERMITTED** and executed (simulated).  
6. Maneuver, renamed tools, and payment wires are **DENIED** — even when the agent claims “I remember I’m authorized.”  
7. A human can elevate a specific effect; only then does execution proceed.  
8. Every decision is written to **Fossil receipts** in CockroachDB (optional S3 mirror).

### CockroachDB tools used (honest)

- **Agent Skills:** `skills/hiop-governed-memory/SKILL.md` encodes fail-closed **memory ≠ authority** for agent runtimes.  
- **ccloud / CockroachDB Cloud:** cluster provisioned and schema applied so memory is truly persistent (see `scripts/ccloud-workflow.md`).  
- **Not claimed in RC1:** Managed MCP Server (example config only); Distributed Vector Indexing product (we use FLOAT8[] + in-app ranking, not CRDB VECTOR index).

### AWS services used

- **AWS Lambda:** serverless execution of the remember → authorize → execute loop (`deploy/aws/handler.py`).  
- **Amazon S3 (optional):** receipt JSON mirror when configured.

### Built with

CockroachDB, AWS Lambda, Amazon S3, Python, HIOP Effect Authority (disclosed pre-existing core)

### Pre-existing work

Disclosed HIOP Effect Authority product core. Contest-period work is the CRDB memory plane, AWS packaging, and governed memory demonstration.

## Built for

CockroachDB × AWS Hackathon – Build with Agentic Memory
