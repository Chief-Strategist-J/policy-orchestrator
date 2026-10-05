"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SQLITE ALGORITHM REGISTRY ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   SQLite3 persistent and in-memory implementation of AlgorithmRegistryPort
   with complete CRUD, upsert semantics, JSON schema validation, and tag filtering.

2. ARCHITECTURAL LOCATION:
   src/infra/adapters/database/sqlite_algorithm_registry_adapter.py
   Adheres to api.structure.working.rule.md Section 3.8.
================================================================================
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any
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
from src.domain.ports.algorithm_registry_port import AlgorithmRegistryPort
from src.infra.adapters.database.migration_runner import DatabaseMigrationRunner


class SQLiteAlgorithmRegistryAdapter(AlgorithmRegistryPort):
    def __init__(self, db_path: str = ":memory:", auto_migrate: bool = True) -> None:
        self.db_path = db_path
        self._memory_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row

        if auto_migrate:
            runner = DatabaseMigrationRunner(f"sqlite:///{db_path}")
            conn = self._get_connection()
            runner.run_migrations(conn)
            runner.seed_algorithm_catalog(conn)

    def _get_connection(self) -> sqlite3.Connection:
        if self._memory_conn is not None:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def register_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        return self.upsert_algorithm(contract)

    def upsert_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
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
                    contract.id,
                    contract.name,
                    contract.version,
                    contract.category.value,
                    json.dumps(contract.capability_tags),
                    json.dumps(contract.input_schema),
                    json.dumps(contract.output_schema),
                    json.dumps(contract.parameters_schema),
                    contract.purity.value,
                    contract.determinism.value,
                    contract.idempotency.value,
                    contract.reversibility.value,
                    contract.side_effects.value,
                    contract.concurrency_model.value,
                    contract.hardware_target.value,
                    contract.complexity.time,
                    contract.complexity.space,
                    json.dumps(contract.preconditions),
                    json.dumps(contract.postconditions),
                    json.dumps(contract.compatible_adapters),
                    1 if contract.is_active else 0,
                ),
            )
            conn.commit()
            return self.get_algorithm(contract.id)  # type: ignore
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def get_algorithm(self, algo_id: str) -> Optional[AlgorithmContract]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM algorithm_registry WHERE id = ?", (algo_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_contract(row)
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def list_algorithms(
        self,
        category: Optional[AlgorithmCategory] = None,
        tags: Optional[List[str]] = None,
        purity: Optional[Purity] = None,
        side_effects: Optional[SideEffectScope] = None,
        is_active: bool = True,
    ) -> List[AlgorithmContract]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM algorithm_registry WHERE is_active = ?"
            params: List[Any] = [1 if is_active else 0]

            if category:
                query += " AND category = ?"
                params.append(category.value)
            if purity:
                query += " AND purity = ?"
                params.append(purity.value)
            if side_effects:
                query += " AND side_effects = ?"
                params.append(side_effects.value)

            query += " ORDER BY id ASC"

            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            contracts = [self._row_to_contract(r) for r in rows]

            if tags:
                contracts = [c for c in contracts if all(t in c.capability_tags for t in tags)]

            return contracts
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def update_algorithm(self, algo_id: str, updates: Dict[str, Any]) -> Optional[AlgorithmContract]:
        conn = self._get_connection()
        try:
            existing = self.get_algorithm(algo_id)
            if not existing:
                return None

            field_mapping = {
                "name": ("name", lambda v: v),
                "version": ("version", lambda v: v),
                "category": ("category", lambda v: v.value if hasattr(v, "value") else str(v)),
                "capability_tags": ("capability_tags", lambda v: json.dumps(list(v))),
                "input_schema": ("input_schema", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else str(v)),
                "output_schema": ("output_schema", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else str(v)),
                "parameters_schema": ("parameters_schema", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else str(v)),
                "purity": ("purity", lambda v: v.value if hasattr(v, "value") else str(v)),
                "determinism": ("determinism", lambda v: v.value if hasattr(v, "value") else str(v)),
                "idempotency": ("idempotency", lambda v: v.value if hasattr(v, "value") else str(v)),
                "reversibility": ("reversibility", lambda v: v.value if hasattr(v, "value") else str(v)),
                "side_effects": ("side_effects", lambda v: v.value if hasattr(v, "value") else str(v)),
                "concurrency_model": ("concurrency_model", lambda v: v.value if hasattr(v, "value") else str(v)),
                "hardware_target": ("hardware_target", lambda v: v.value if hasattr(v, "value") else str(v)),
                "time_complexity": ("time_complexity", lambda v: str(v)),
                "space_complexity": ("space_complexity", lambda v: str(v)),
                "preconditions": ("preconditions", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else str(v)),
                "postconditions": ("postconditions", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else str(v)),
                "compatible_adapters": ("compatible_adapters", lambda v: json.dumps(list(v))),
                "is_active": ("is_active", lambda v: 1 if v else 0),
            }

            set_clauses = []
            set_params = []
            for k, val in updates.items():
                if k in field_mapping:
                    col_name, transform = field_mapping[k]
                    set_clauses.append(f"{col_name} = ?")
                    set_params.append(transform(val))

            if not set_clauses:
                return existing

            set_clauses.append("updated_at = datetime('now')")
            sql = f"UPDATE algorithm_registry SET {', '.join(set_clauses)} WHERE id = ?"
            set_params.append(algo_id)

            cursor = conn.cursor()
            cursor.execute(sql, tuple(set_params))
            conn.commit()

            return self.get_algorithm(algo_id)
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def delete_algorithm(self, algo_id: str, hard_delete: bool = False) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if hard_delete:
                cursor.execute("DELETE FROM algorithm_registry WHERE id = ?", (algo_id,))
            else:
                cursor.execute("UPDATE algorithm_registry SET is_active = 0, updated_at = datetime('now') WHERE id = ?", (algo_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def register_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        return self.upsert_adapter(adapter)

    def upsert_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
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
            return adapter
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, source_type, target_type, algo_id, is_lossy, description FROM type_adapters WHERE source_type = ? AND target_type = ?",
                (source_type, target_type),
            )
            rows = cursor.fetchall()
            return [
                TypeAdapterContract(
                    id=r["id"],
                    name=r["name"],
                    source_type=r["source_type"],
                    target_type=r["target_type"],
                    algo_id=r["algo_id"],
                    is_lossy=bool(r["is_lossy"]),
                    description=r["description"],
                )
                for r in rows
            ]
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def list_adapters(self) -> List[TypeAdapterContract]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, source_type, target_type, algo_id, is_lossy, description FROM type_adapters ORDER BY id ASC")
            rows = cursor.fetchall()
            return [
                TypeAdapterContract(
                    id=r["id"],
                    name=r["name"],
                    source_type=r["source_type"],
                    target_type=r["target_type"],
                    algo_id=r["algo_id"],
                    is_lossy=bool(r["is_lossy"]),
                    description=r["description"],
                )
                for r in rows
            ]
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def delete_adapter(self, adapter_id: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM type_adapters WHERE id = ?", (adapter_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            if conn is not self._memory_conn:
                conn.close()

    def _row_to_contract(self, row: sqlite3.Row) -> AlgorithmContract:
        return AlgorithmContract(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            category=AlgorithmCategory(row["category"]),
            capability_tags=json.loads(row["capability_tags"]),
            input_schema=json.loads(row["input_schema"]),
            output_schema=json.loads(row["output_schema"]),
            parameters_schema=json.loads(row["parameters_schema"] or "{}"),
            purity=Purity(row["purity"]),
            determinism=Determinism(row["determinism"]),
            idempotency=Idempotency(row["idempotency"]),
            reversibility=Reversibility(row["reversibility"]),
            side_effects=SideEffectScope(row["side_effects"]),
            concurrency_model=ConcurrencyModel(row["concurrency_model"]),
            hardware_target=HardwareTarget(row["hardware_target"]),
            complexity=ComplexityCost(time=row["time_complexity"], space=row["space_complexity"]),
            preconditions=json.loads(row["preconditions"] or "[]"),
            postconditions=json.loads(row["postconditions"] or "[]"),
            compatible_adapters=json.loads(row["compatible_adapters"] or "[]"),
            is_active=bool(row["is_active"]),
        )
