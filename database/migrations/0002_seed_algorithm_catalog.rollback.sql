-- rollback_migration: 0002
-- description:        clear seeded algorithm catalog and type adapters (PostgreSQL / Google AlloyDB Omni)
-- author:             Antigravity / Lead Software Engineer
-- date:               2026-10-05

TRUNCATE TABLE type_adapters CASCADE;
TRUNCATE TABLE algorithm_registry CASCADE;
DELETE FROM schema_migrations WHERE version = '0002';
