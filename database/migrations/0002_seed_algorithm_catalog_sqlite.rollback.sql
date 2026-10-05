-- rollback_migration: 0002
-- description:        clear seeded algorithm catalog and type adapters (SQLite)
-- author:             Antigravity / Lead Software Engineer
-- date:               2026-10-05

DELETE FROM type_adapters;
DELETE FROM algorithm_registry;
DELETE FROM schema_migrations WHERE version = '0002';
