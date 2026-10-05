"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNIT TESTS FOR DATABASE MIGRATION RUNNER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests database migration DDL execution, table creation, and algorithm catalog
   seeding for the Layer 1 Capability Registry.
================================================================================
"""

import sqlite3
import pytest
from src.infra.adapters.database import DatabaseMigrationRunner



def test_sqlite_migration_and_seeding(tmp_path):
    db_file = tmp_path / "test_policy_registry.db"
    db_url = f"sqlite:///{db_file}"

    runner = DatabaseMigrationRunner(db_url)
    runner.run_migrations()

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "algorithm_registry" in tables
    assert "type_adapters" in tables
    assert "execution_workflows" in tables

    # Seed algorithms
    count = runner.seed_algorithm_catalog(conn)
    assert count == 56

    cursor.execute("SELECT COUNT(*) FROM algorithm_registry")
    assert cursor.fetchone()[0] == 56

    cursor.execute("SELECT COUNT(*) FROM type_adapters")
    assert cursor.fetchone()[0] == 11

    # Idempotent re-seeding
    count2 = runner.seed_algorithm_catalog(conn)
    assert count2 == 56
    cursor.execute("SELECT COUNT(*) FROM algorithm_registry")
    assert cursor.fetchone()[0] == 56

    conn.close()


def test_migration_sql_files_exist():
    runner = DatabaseMigrationRunner()
    pg_candidates = [
        runner.migrations_dir / "0001_create_algorithm_registry_table.sql",
        runner.migrations_dir / "001_create_algorithm_registry.sql",
    ]
    sqlite_candidates = [
        runner.migrations_dir / "0001_create_algorithm_registry_sqlite.sql",
        runner.migrations_dir / "001_create_algorithm_registry_sqlite.sql",
    ]

    pg_migration = next((c for c in pg_candidates if c.exists()), None)
    sqlite_migration = next((c for c in sqlite_candidates if c.exists()), None)

    assert pg_migration is not None and pg_migration.exists()
    assert sqlite_migration is not None and sqlite_migration.exists()

    pg_sql = pg_migration.read_text()
    assert "CREATE TABLE IF NOT EXISTS algorithm_registry" in pg_sql
    assert "CREATE INDEX IF NOT EXISTS idx_algo_tags" in pg_sql

    sqlite_sql = sqlite_migration.read_text()
    assert "CREATE TABLE IF NOT EXISTS algorithm_registry" in sqlite_sql
