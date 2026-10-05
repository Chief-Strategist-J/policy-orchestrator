-- rollback_migration: 0001
-- description:        drop algorithm registry and type adapters tables
-- author:             Antigravity / Lead Software Engineer
-- date:               2026-10-05

DROP TABLE IF EXISTS execution_workflows CASCADE;
DROP TABLE IF EXISTS type_adapters CASCADE;
DROP TABLE IF EXISTS algorithm_registry CASCADE;
