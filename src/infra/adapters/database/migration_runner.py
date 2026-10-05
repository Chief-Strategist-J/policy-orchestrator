"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DATABASE MIGRATION & SEED RUNNER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Automated database schema migration and algorithm catalog seeder.
   Supports both Google AlloyDB Omni / PostgreSQL and SQLite.

2. ARCHITECTURAL LOCATION:
   src/infra/database/migrations/migration_runner.py
   Adheres to api.structure.working.rule.md Section 3.8 and database/migration.md.
================================================================================
"""

import os
import json
import sqlite3
from typing import Optional, Any
from pathlib import Path

from src.domain.models.algorithm_contract import AlgorithmContract, TypeAdapterContract
from src.features.code_engine.registry.algorithm_catalog import (
    BUILTIN_ALGORITHM_CONTRACTS,
    BUILTIN_TYPE_ADAPTERS,
)


class DatabaseMigrationRunner:
    def __init__(self, db_url: Optional[str] = None) -> None:
        self.db_url = db_url or os.environ.get("DATABASE_URL", "sqlite:///:memory:")
        
        # Single Source of Truth for migrations: database/migrations/ at sub-package root
        self.migrations_dir = Path(__file__).resolve().parents[4] / "database" / "migrations"

    def is_postgres(self) -> bool:
        return self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://")

    def run_migrations(self, conn: Optional[Any] = None) -> None:
        if self.is_postgres():
            self._run_postgres_migrations(conn)
        else:
            self._run_sqlite_migrations(conn)

    def _run_sqlite_migrations(self, conn: Optional[sqlite3.Connection] = None) -> None:
        close_conn = False
        if conn is None:
            db_path = self.db_url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            close_conn = True

        migration_file = self.migrations_dir / "0001_create_algorithm_registry_sqlite.sql"
        if not migration_file.exists():
            raise FileNotFoundError(f"SQLite migration file missing at: {migration_file}")

        sql = migration_file.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()

        if close_conn:
            conn.close()

    def _run_postgres_migrations(self, conn: Optional[Any] = None) -> None:
        import psycopg2

        close_conn = False
        if conn is None:
            conn = psycopg2.connect(self.db_url)
            close_conn = True

        migration_file = self.migrations_dir / "0001_create_algorithm_registry_table.sql"
        if not migration_file.exists():
            raise FileNotFoundError(f"PostgreSQL migration file missing at: {migration_file}")

        sql = migration_file.read_text(encoding="utf-8")

        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        if close_conn:
            conn.close()

    def seed_algorithm_catalog(self, conn: Optional[Any] = None) -> int:
        if self.is_postgres():
            return self._seed_postgres(conn)
        else:
            return self._seed_sqlite(conn)

    def _seed_sqlite(self, conn: Optional[sqlite3.Connection] = None) -> int:
        close_conn = False
        if conn is None:
            db_path = self.db_url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            close_conn = True

        cursor = conn.cursor()
        inserted_count = 0

        for algo in BUILTIN_ALGORITHM_CONTRACTS:
            cursor.execute(
                """
                INSERT INTO algorithm_registry (
                    id, name, version, category, capability_tags,
                    input_schema, output_schema, parameters_schema,
                    purity, determinism, idempotency, reversibility, side_effects,
                    concurrency_model, hardware_target, time_complexity, space_complexity,
                    preconditions, postconditions, compatible_adapters, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    version=excluded.version,
                    category=excluded.category,
                    capability_tags=excluded.capability_tags,
                    input_schema=excluded.input_schema,
                    output_schema=excluded.output_schema,
                    parameters_schema=excluded.parameters_schema,
                    purity=excluded.purity,
                    determinism=excluded.determinism,
                    idempotency=excluded.idempotency,
                    reversibility=excluded.reversibility,
                    side_effects=excluded.side_effects,
                    concurrency_model=excluded.concurrency_model,
                    hardware_target=excluded.hardware_target,
                    time_complexity=excluded.time_complexity,
                    space_complexity=excluded.space_complexity,
                    preconditions=excluded.preconditions,
                    postconditions=excluded.postconditions,
                    compatible_adapters=excluded.compatible_adapters,
                    is_active=excluded.is_active,
                    updated_at=datetime('now')
                """,
                (
                    algo.id,
                    algo.name,
                    algo.version,
                    algo.category.value,
                    json.dumps(algo.capability_tags),
                    json.dumps(algo.input_schema),
                    json.dumps(algo.output_schema),
                    json.dumps(algo.parameters_schema),
                    algo.purity.value,
                    algo.determinism.value,
                    algo.idempotency.value,
                    algo.reversibility.value,
                    algo.side_effects.value,
                    algo.concurrency_model.value,
                    algo.hardware_target.value,
                    algo.complexity.time,
                    algo.complexity.space,
                    json.dumps(algo.preconditions),
                    json.dumps(algo.postconditions),
                    json.dumps(algo.compatible_adapters),
                    1 if algo.is_active else 0,
                ),
            )
            inserted_count += 1

        for adapter in BUILTIN_TYPE_ADAPTERS:
            cursor.execute(
                """
                INSERT INTO type_adapters (
                    id, name, source_type, target_type, algo_id, is_lossy, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    source_type=excluded.source_type,
                    target_type=excluded.target_type,
                    algo_id=excluded.algo_id,
                    is_lossy=excluded.is_lossy,
                    description=excluded.description
                """,
                (
                    adapter.id,
                    adapter.name,
                    adapter.source_type,
                    adapter.target_type,
                    adapter.algo_id,
                    1 if adapter.is_lossy else 0,
                    adapter.description,
                ),
            )

        conn.commit()
        if close_conn:
            conn.close()

        return inserted_count

    def _seed_postgres(self, conn: Optional[Any] = None) -> int:
        import psycopg2

        close_conn = False
        if conn is None:
            conn = psycopg2.connect(self.db_url)
            close_conn = True

        inserted_count = 0
        with conn.cursor() as cur:
            for algo in BUILTIN_ALGORITHM_CONTRACTS:
                cur.execute(
                    """
                    INSERT INTO algorithm_registry (
                        id, name, version, category, capability_tags,
                        input_schema, output_schema, parameters_schema,
                        purity, determinism, idempotency, reversibility, side_effects,
                        concurrency_model, hardware_target, time_complexity, space_complexity,
                        preconditions, postconditions, compatible_adapters, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id) DO UPDATE SET
                        name=EXCLUDED.name,
                        version=EXCLUDED.version,
                        category=EXCLUDED.category,
                        capability_tags=EXCLUDED.capability_tags,
                        input_schema=EXCLUDED.input_schema,
                        output_schema=EXCLUDED.output_schema,
                        parameters_schema=EXCLUDED.parameters_schema,
                        purity=EXCLUDED.purity,
                        determinism=EXCLUDED.determinism,
                        idempotency=EXCLUDED.idempotency,
                        reversibility=EXCLUDED.reversibility,
                        side_effects=EXCLUDED.side_effects,
                        concurrency_model=EXCLUDED.concurrency_model,
                        hardware_target=EXCLUDED.hardware_target,
                        time_complexity=EXCLUDED.time_complexity,
                        space_complexity=EXCLUDED.space_complexity,
                        preconditions=EXCLUDED.preconditions,
                        postconditions=EXCLUDED.postconditions,
                        compatible_adapters=EXCLUDED.compatible_adapters,
                        is_active=EXCLUDED.is_active,
                        updated_at=NOW()
                    """,
                    (
                        algo.id,
                        algo.name,
                        algo.version,
                        algo.category.value,
                        algo.capability_tags,
                        json.dumps(algo.input_schema),
                        json.dumps(algo.output_schema),
                        json.dumps(algo.parameters_schema),
                        algo.purity.value,
                        algo.determinism.value,
                        algo.idempotency.value,
                        algo.reversibility.value,
                        algo.side_effects.value,
                        algo.concurrency_model.value,
                        algo.hardware_target.value,
                        algo.complexity.time,
                        algo.complexity.space,
                        json.dumps(algo.preconditions),
                        json.dumps(algo.postconditions),
                        algo.compatible_adapters,
                        algo.is_active,
                    ),
                )
                inserted_count += 1

            for adapter in BUILTIN_TYPE_ADAPTERS:
                cur.execute(
                    """
                    INSERT INTO type_adapters (
                        id, name, source_type, target_type, algo_id, is_lossy, description
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT(id) DO UPDATE SET
                        name=EXCLUDED.name,
                        source_type=EXCLUDED.source_type,
                        target_type=EXCLUDED.target_type,
                        algo_id=EXCLUDED.algo_id,
                        is_lossy=EXCLUDED.is_lossy,
                        description=EXCLUDED.description
                    """,
                    (
                        adapter.id,
                        adapter.name,
                        adapter.source_type,
                        adapter.target_type,
                        adapter.algo_id,
                        adapter.is_lossy,
                        adapter.description,
                    ),
                )

        conn.commit()
        if close_conn:
            conn.close()

        return inserted_count

    def seed_catalog(self, conn: Optional[Any] = None) -> int:
        return self.seed_algorithm_catalog(conn)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Database Migration & Catalog Seeder CLI")
    parser.add_argument(
        "action",
        choices=["migrate", "seed", "run-all"],
        help="Action to execute: migrate schema, seed catalog, or run-all",
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL", "sqlite:///:memory:"),
        help="Target database URL (e.g. postgresql://... or sqlite:///...)",
    )

    args = parser.parse_args()
    runner = DatabaseMigrationRunner(db_url=args.db_url)

    if args.action in ["migrate", "run-all"]:
        print(f"Applying schema migrations from {runner.migrations_dir}...")
        runner.run_migrations()
        print("Schema migrations applied successfully.")

    if args.action in ["seed", "run-all"]:
        print("Seeding builtin algorithm contracts and type adapters...")
        count = runner.seed_algorithm_catalog()
        print(f"Successfully seeded {count} algorithm contracts & type adapters.")

    print("Operation completed successfully.")
