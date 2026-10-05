"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DATABASE MIGRATION & SEED RUNNER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Automated database schema migration, rollback, status tracking, and
   algorithm catalog seeder supporting Google AlloyDB Omni, PostgreSQL, and SQLite.
   Implements idempotent upsert semantics (ON CONFLICT DO UPDATE) and
   100% contract parity verification.

2. ARCHITECTURAL LOCATION:
   src/infra/adapters/database/migration_runner.py
   Adheres to api.structure.working.rule.md Section 3.8.
================================================================================
"""

import os
import json
import sqlite3
from typing import Optional, Any, Dict, List
from pathlib import Path

from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    TypeAdapterContract,
    AlgorithmCategory,
    Purity,
    Determinism,
    Idempotency,
    Reversibility,
    SideEffectScope,
    ConcurrencyModel,
    HardwareTarget,
    ComplexityCost,
)
from src.features.code_engine.registry.algorithm_catalog import (
    BUILTIN_ALGORITHM_CONTRACTS,
    BUILTIN_TYPE_ADAPTERS,
)


class DatabaseMigrationRunner:
    def __init__(self, db_url: Optional[str] = None) -> None:
        self.db_url = db_url or os.environ.get("DATABASE_URL", "sqlite:///:memory:")
        self.migrations_dir = Path(__file__).resolve().parents[4] / "database" / "migrations"

    def is_postgres(self) -> bool:
        return self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://")

    def run_migrations(self, conn: Optional[Any] = None) -> Dict[str, Any]:
        if self.is_postgres():
            return self._run_postgres_migrations(conn)
        else:
            return self._run_sqlite_migrations(conn)

    def rollback_migrations(self, conn: Optional[Any] = None) -> Dict[str, Any]:
        if self.is_postgres():
            return self._rollback_postgres_migrations(conn)
        else:
            return self._rollback_sqlite_migrations(conn)

    def _run_sqlite_migrations(self, conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
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

        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, name) VALUES (?, ?)",
            ("0001", "create_algorithm_registry_sqlite"),
        )
        conn.commit()

        if close_conn:
            conn.close()

        return {"status": "success", "applied_version": "0001", "db": "sqlite"}

    def _rollback_sqlite_migrations(self, conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
        close_conn = False
        if conn is None:
            db_path = self.db_url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            close_conn = True

        rollback_file = self.migrations_dir / "0001_create_algorithm_registry_sqlite.rollback.sql"
        if not rollback_file.exists():
            raise FileNotFoundError(f"SQLite rollback file missing at: {rollback_file}")

        sql = rollback_file.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()

        if close_conn:
            conn.close()

        return {"status": "success", "rolled_back_version": "0001", "db": "sqlite"}

    def _run_postgres_migrations(self, conn: Optional[Any] = None) -> Dict[str, Any]:
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
            cur.execute(
                """
                INSERT INTO schema_migrations (version, name)
                VALUES (%s, %s)
                ON CONFLICT (version) DO NOTHING
                """,
                ("0001", "create_algorithm_registry_table"),
            )
        conn.commit()

        if close_conn:
            conn.close()

        return {"status": "success", "applied_version": "0001", "db": "postgres"}

    def _rollback_postgres_migrations(self, conn: Optional[Any] = None) -> Dict[str, Any]:
        import psycopg2

        close_conn = False
        if conn is None:
            conn = psycopg2.connect(self.db_url)
            close_conn = True

        rollback_file = self.migrations_dir / "0001_create_algorithm_registry_table.rollback.sql"
        if not rollback_file.exists():
            raise FileNotFoundError(f"PostgreSQL rollback file missing at: {rollback_file}")

        sql = rollback_file.read_text(encoding="utf-8")

        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

        if close_conn:
            conn.close()

        return {"status": "success", "rolled_back_version": "0001", "db": "postgres"}

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

    def get_migration_status(self, conn: Optional[Any] = None) -> Dict[str, Any]:
        if self.is_postgres():
            import psycopg2
            close_conn = False
            if conn is None:
                conn = psycopg2.connect(self.db_url)
                close_conn = True
            with conn.cursor() as cur:
                cur.execute("SELECT version, name, applied_at FROM schema_migrations ORDER BY version ASC")
                rows = cur.fetchall()
            if close_conn:
                conn.close()
            return {"applied": [{"version": r[0], "name": r[1], "applied_at": str(r[2])} for r in rows]}
        else:
            close_conn = False
            if conn is None:
                db_path = self.db_url.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path)
                close_conn = True
            cursor = conn.cursor()
            cursor.execute("SELECT version, name, applied_at FROM schema_migrations ORDER BY version ASC")
            rows = cursor.fetchall()
            if close_conn:
                conn.close()
            return {"applied": [{"version": r[0], "name": r[1], "applied_at": str(r[2])} for r in rows]}

    def verify_database_parity(self, conn: Optional[Any] = None) -> Dict[str, Any]:
        if self.is_postgres():
            from src.infra.adapters.database.alloydb_algorithm_registry_adapter import AlloyDBAlgorithmRegistryAdapter
            adapter = AlloyDBAlgorithmRegistryAdapter(self.db_url)
        else:
            from src.infra.adapters.database.sqlite_algorithm_registry_adapter import SQLiteAlgorithmRegistryAdapter
            db_path = self.db_url.replace("sqlite:///", "")
            adapter = SQLiteAlgorithmRegistryAdapter(db_path, auto_migrate=False)

        db_algos = {a.id: a for a in adapter.list_algorithms(is_active=True)}
        code_algos = {a.id: a for a in BUILTIN_ALGORITHM_CONTRACTS if a.is_active}

        missing_in_db = set(code_algos.keys()) - set(db_algos.keys())
        extra_in_db = set(db_algos.keys()) - set(code_algos.keys())
        mismatches = []

        for aid, code_algo in code_algos.items():
            if aid in db_algos:
                db_algo = db_algos[aid]
                if code_algo.name != db_algo.name or code_algo.category != db_algo.category or code_algo.complexity.time != db_algo.complexity.time:
                    mismatches.append({"id": aid, "reason": "attribute_difference"})

        return {
            "total_code_algorithms": len(code_algos),
            "total_db_algorithms": len(db_algos),
            "parity_matched": len(missing_in_db) == 0 and len(extra_in_db) == 0 and len(mismatches) == 0,
            "missing_in_db": list(missing_in_db),
            "extra_in_db": list(extra_in_db),
            "mismatches": mismatches,
        }

    def seed_catalog(self, conn: Optional[Any] = None) -> int:
        return self.seed_algorithm_catalog(conn)
