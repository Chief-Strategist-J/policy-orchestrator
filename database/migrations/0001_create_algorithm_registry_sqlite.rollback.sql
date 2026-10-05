-- rollback_migration: 0001
-- description:        drop algorithm registry, type adapters, and execution workflows tables (SQLite)
-- author:             Antigravity / Lead Software Engineer
-- date:               2026-10-05

DROP TABLE IF EXISTS execution_workflows;
DROP TABLE IF EXISTS type_adapters;
DROP TABLE IF EXISTS algorithm_registry;
DROP TABLE IF EXISTS schema_migrations;
