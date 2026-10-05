-- migration:      0001
-- description:    create algorithm registry and type adapters tables (SQLite)
-- author:         Antigravity / Lead Software Engineer
-- date:           2026-10-05
-- depends_on:     NONE
-- reversible:     YES
-- lock_risk:      LOW

CREATE TABLE IF NOT EXISTS algorithm_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    category TEXT NOT NULL,
    capability_tags TEXT NOT NULL DEFAULT '[]',
    input_schema TEXT NOT NULL,
    output_schema TEXT NOT NULL,
    parameters_schema TEXT NOT NULL DEFAULT '{}',
    purity TEXT NOT NULL CHECK (purity IN ('PURE', 'IMPURE')),
    determinism TEXT NOT NULL CHECK (determinism IN ('DETERMINISTIC', 'STOCHASTIC')),
    idempotency TEXT NOT NULL CHECK (idempotency IN ('IDEMPOTENT', 'NON_IDEMPOTENT')),
    reversibility TEXT NOT NULL CHECK (reversibility IN ('REVERSIBLE', 'IRREVERSIBLE')),
    side_effects TEXT NOT NULL CHECK (side_effects IN ('READ_ONLY', 'IN_MEMORY', 'DISK_WRITE', 'NETWORK_IO')),
    concurrency_model TEXT NOT NULL DEFAULT 'THREAD_SAFE',
    hardware_target TEXT NOT NULL DEFAULT 'CPU_SCALAR',
    time_complexity TEXT NOT NULL,
    space_complexity TEXT NOT NULL,
    preconditions TEXT NOT NULL DEFAULT '[]',
    postconditions TEXT NOT NULL DEFAULT '[]',
    compatible_adapters TEXT NOT NULL DEFAULT '[]',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_algo_category ON algorithm_registry (category);
CREATE INDEX IF NOT EXISTS idx_algo_purity ON algorithm_registry (purity);
CREATE INDEX IF NOT EXISTS idx_algo_side_effects ON algorithm_registry (side_effects);

CREATE TABLE IF NOT EXISTS type_adapters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    algo_id TEXT,
    is_lossy INTEGER NOT NULL DEFAULT 0,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(algo_id) REFERENCES algorithm_registry(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_adapters_source_target ON type_adapters (source_type, target_type);

CREATE TABLE IF NOT EXISTS execution_workflows (
    run_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    goal TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'COMPENSATED')),
    execution_dag TEXT NOT NULL,
    current_step_index INTEGER NOT NULL DEFAULT 0,
    checkpoints TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_workflow_trace ON execution_workflows(trace_id);
