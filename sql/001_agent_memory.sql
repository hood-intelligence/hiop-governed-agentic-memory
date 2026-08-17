-- HIOP × CockroachDB agentic memory
-- Qualifying tools:
--   1) Distributed Vector Indexing — VECTOR(8) + VECTOR INDEX + <-> search
--   2) Agent Skills — enforced in app (skills/hiop-governed-memory)
-- Memory NEVER stores authority grants.

CREATE TABLE IF NOT EXISTS agent_episodes (
  episode_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id     STRING NOT NULL,
  tenant_id    STRING NOT NULL,
  kind         STRING NOT NULL,
  content      JSONB NOT NULL,
  -- CockroachDB Distributed Vector Indexing (VECTOR type)
  embedding    VECTOR(8) NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_authority BOOL NOT NULL DEFAULT false CHECK (is_authority = false)
);

-- Distributed vector index (CRDB 25.2+ / Cloud current)
-- Prefix agent_id pre-filters search space per agent.
CREATE VECTOR INDEX IF NOT EXISTS idx_agent_episodes_embedding
  ON agent_episodes (agent_id, embedding);

CREATE INDEX IF NOT EXISTS idx_agent_episodes_agent_time
  ON agent_episodes (agent_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_episodes_kind
  ON agent_episodes (kind);

CREATE TABLE IF NOT EXISTS agent_task_state (
  task_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id     STRING NOT NULL,
  tenant_id    STRING NOT NULL,
  goal         STRING NOT NULL,
  status       STRING NOT NULL DEFAULT 'open',
  context      JSONB NOT NULL DEFAULT '{}',
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fossil_receipts (
  receipt_id   STRING PRIMARY KEY,
  agent_id     STRING NOT NULL,
  outcome      STRING NOT NULL,
  effect_id    STRING NULL,
  payload      JSONB NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS policy_envelopes (
  agent_id        STRING PRIMARY KEY,
  owner           STRING NOT NULL,
  tenant_id       STRING NOT NULL,
  allowed_effects STRING[] NOT NULL,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Skill application audit (Agent Skills participation evidence)
CREATE TABLE IF NOT EXISTS skill_applications (
  application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id       STRING NOT NULL,
  skill_id       STRING NOT NULL,
  skill_version  STRING NOT NULL,
  rules_applied  JSONB NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO policy_envelopes (agent_id, owner, tenant_id, allowed_effects)
VALUES
  ('ops-memory-agent', 'owner-mission', 'tenant-mission',
   ARRAY['telemetry.analyze', 'lab.adjust_setpoint'])
ON CONFLICT (agent_id) DO NOTHING;
