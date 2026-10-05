-- migration:      0001
-- description:    create algorithm registry and type adapters tables
-- author:         Antigravity / Lead Software Engineer
-- date:           2026-10-05
-- depends_on:     NONE
-- reversible:     YES
-- lock_risk:      LOW
-- rows_affected:  0 (schema creation)
-- reason:         Layer 1 algorithm capability registry and type adapter storage

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Capability & Algorithm Contract Registry (Layer 1 G1-G3)
CREATE TABLE IF NOT EXISTS algorithm_registry (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
    category VARCHAR(64) NOT NULL,
    capability_tags TEXT[] NOT NULL DEFAULT '{}',
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    parameters_schema JSONB NOT NULL DEFAULT '{}',
    purity VARCHAR(16) NOT NULL CHECK (purity IN ('PURE', 'IMPURE')),
    determinism VARCHAR(16) NOT NULL CHECK (determinism IN ('DETERMINISTIC', 'STOCHASTIC')),
    idempotency VARCHAR(16) NOT NULL CHECK (idempotency IN ('IDEMPOTENT', 'NON_IDEMPOTENT')),
    reversibility VARCHAR(16) NOT NULL CHECK (reversibility IN ('REVERSIBLE', 'IRREVERSIBLE')),
    side_effects VARCHAR(32) NOT NULL CHECK (side_effects IN ('READ_ONLY', 'IN_MEMORY', 'DISK_WRITE', 'NETWORK_IO')),
    concurrency_model VARCHAR(32) NOT NULL DEFAULT 'THREAD_SAFE',
    hardware_target VARCHAR(32) NOT NULL DEFAULT 'CPU_SCALAR',
    time_complexity VARCHAR(64) NOT NULL,
    space_complexity VARCHAR(64) NOT NULL,
    preconditions JSONB NOT NULL DEFAULT '[]',
    postconditions JSONB NOT NULL DEFAULT '[]',
    compatible_adapters TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_algo_tags ON algorithm_registry USING GIN (capability_tags);
CREATE INDEX IF NOT EXISTS idx_algo_category ON algorithm_registry (category);
CREATE INDEX IF NOT EXISTS idx_algo_purity ON algorithm_registry (purity);
CREATE INDEX IF NOT EXISTS idx_algo_side_effects ON algorithm_registry (side_effects);

-- 2. Adapter Registry (Layer 1 G4)
CREATE TABLE IF NOT EXISTS type_adapters (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    target_type VARCHAR(64) NOT NULL,
    algo_id VARCHAR(64) REFERENCES algorithm_registry(id) ON DELETE SET NULL,
    is_lossy BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_adapters_source_target ON type_adapters (source_type, target_type);

-- 3. Execution Workflows & Checkpoints (Layer 4 G37)
CREATE TABLE IF NOT EXISTS execution_workflows (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(64) NOT NULL,
    goal TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'COMPENSATED')),
    execution_dag JSONB NOT NULL,
    current_step_index INT NOT NULL DEFAULT 0,
    checkpoints JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_trace ON execution_workflows(trace_id);
