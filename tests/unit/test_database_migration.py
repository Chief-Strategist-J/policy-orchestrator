"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNIT TESTS FOR DATABASE MIGRATION RUNNER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests database migration DDL execution, table creation, schema tracking,
   rollback mechanics, algorithm catalog seeding, and 100% parity verification.
================================================================================
"""

import sqlite3
import pytest
from src.infra.adapters.database import DatabaseMigrationRunner, SQLiteAlgorithmRegistryAdapter
from src.features.code_engine.registry.algorithm_catalog import BUILTIN_ALGORITHM_CONTRACTS, BUILTIN_TYPE_ADAPTERS


def test_sqlite_migration_and_seeding(tmp_path):
    db_file = tmp_path / "test_policy_registry.db"
    db_url = f"sqlite:///{db_file}"

    runner = DatabaseMigrationRunner(db_url)
    res = runner.run_migrations()
    assert res["status"] == "success"

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "schema_migrations" in tables
    assert "algorithm_registry" in tables
    assert "type_adapters" in tables
    assert "execution_workflows" in tables

    # Check migration tracking
    status = runner.get_migration_status(conn)
    assert len(status["applied"]) >= 1
    assert status["applied"][0]["version"] == "0001"

    # Seed algorithms
    count = runner.seed_algorithm_catalog(conn)
    assert count == 242

    cursor.execute("SELECT COUNT(*) FROM algorithm_registry")
    assert cursor.fetchone()[0] == 242

    cursor.execute("SELECT COUNT(*) FROM type_adapters")
    assert cursor.fetchone()[0] == 11

    # Idempotent re-seeding
    count2 = runner.seed_algorithm_catalog(conn)
    assert count2 == 242
    cursor.execute("SELECT COUNT(*) FROM algorithm_registry")
    assert cursor.fetchone()[0] == 242

    # Parity check
    parity = runner.verify_database_parity(conn)
    assert parity.get("parity_matched") is True
    assert parity["total_code_algorithms"] == 242
    assert parity["total_db_algorithms"] == 242

    conn.close()


def test_sqlite_migration_rollback_and_reapply(tmp_path):
    db_file = tmp_path / "test_rollback.db"
    db_url = f"sqlite:///{db_file}"

    runner = DatabaseMigrationRunner(db_url)
    runner.run_migrations()
    runner.seed_algorithm_catalog()

    rollback_res = runner.rollback_migrations()
    assert rollback_res["status"] == "success"

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "algorithm_registry" not in tables
    assert "type_adapters" not in tables
    conn.close()

    # Re-apply
    reapply_res = runner.run_migrations()
    assert reapply_res["status"] == "success"
    seeded = runner.seed_algorithm_catalog()
    assert seeded == 242


def test_migration_sql_files_exist():
    runner = DatabaseMigrationRunner()
    pg_candidates = [
        runner.migrations_dir / "0001_create_algorithm_registry_table.sql",
    ]
    sqlite_candidates = [
        runner.migrations_dir / "0001_create_algorithm_registry_sqlite.sql",
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
