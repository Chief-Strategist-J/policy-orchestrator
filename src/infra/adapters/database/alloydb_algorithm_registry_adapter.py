"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ALLOYDB / POSTGRESQL ALGORITHM REGISTRY ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Enterprise-grade database adapter for Google AlloyDB Omni / PostgreSQL 15+
   supporting GIN-indexed tag arrays, JSONB schema querying, and full ACID
   Layer 1 Algorithm Registry operations.

2. ARCHITECTURAL LOCATION:
   src/infra/adapters/database/alloydb_algorithm_registry_adapter.py
   Adheres to api.structure.working.rule.md Section 3.8.
================================================================================
"""

import json
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


class AlloyDBAlgorithmRegistryAdapter(AlgorithmRegistryPort):
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url.replace("@localhost:", "@127.0.0.1:")
        self._conn = None

    def _get_connection(self):
        import psycopg2
        if self._conn is None or self._conn.closed != 0:
            self._conn = psycopg2.connect(self.db_url)
        return self._conn

    def register_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        return self.upsert_algorithm(contract)

    def upsert_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
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
                    RETURNING *
                    """,
                    (
                        contract.id,
                        contract.name,
                        contract.version,
                        contract.category.value,
                        contract.capability_tags,
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
                        contract.compatible_adapters,
                        contract.is_active,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
            return self._row_to_contract(row, cur.description)
        except Exception:
            conn.rollback()
            raise

    def get_algorithm(self, algo_id: str) -> Optional[AlgorithmContract]:
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM algorithm_registry WHERE id = %s", (algo_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_contract(row, cur.description)

    def list_algorithms(
        self,
        category: Optional[AlgorithmCategory] = None,
        tags: Optional[List[str]] = None,
        purity: Optional[Purity] = None,
        side_effects: Optional[SideEffectScope] = None,
        is_active: bool = True,
    ) -> List[AlgorithmContract]:
        conn = self._get_connection()
        query = "SELECT * FROM algorithm_registry WHERE is_active = %s"
        params: List[Any] = [is_active]

        if category:
            query += " AND category = %s"
            params.append(category.value)
        if purity:
            query += " AND purity = %s"
            params.append(purity.value)
        if side_effects:
            query += " AND side_effects = %s"
            params.append(side_effects.value)
        if tags:
            query += " AND capability_tags @> %s"
            params.append(tags)

        query += " ORDER BY id ASC"

        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            return [self._row_to_contract(r, cur.description) for r in rows]

    def update_algorithm(self, algo_id: str, updates: Dict[str, Any]) -> Optional[AlgorithmContract]:
        conn = self._get_connection()
        existing = self.get_algorithm(algo_id)
        if not existing:
            return None

        field_mapping = {
            "name": ("name", lambda v: v),
            "version": ("version", lambda v: v),
            "category": ("category", lambda v: v.value if hasattr(v, "value") else str(v)),
            "capability_tags": ("capability_tags", lambda v: list(v)),
            "input_schema": ("input_schema", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v),
            "output_schema": ("output_schema", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v),
            "parameters_schema": ("parameters_schema", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v),
            "purity": ("purity", lambda v: v.value if hasattr(v, "value") else str(v)),
            "determinism": ("determinism", lambda v: v.value if hasattr(v, "value") else str(v)),
            "idempotency": ("idempotency", lambda v: v.value if hasattr(v, "value") else str(v)),
            "reversibility": ("reversibility", lambda v: v.value if hasattr(v, "value") else str(v)),
            "side_effects": ("side_effects", lambda v: v.value if hasattr(v, "value") else str(v)),
            "concurrency_model": ("concurrency_model", lambda v: v.value if hasattr(v, "value") else str(v)),
            "hardware_target": ("hardware_target", lambda v: v.value if hasattr(v, "value") else str(v)),
            "time_complexity": ("time_complexity", lambda v: str(v)),
            "space_complexity": ("space_complexity", lambda v: str(v)),
            "preconditions": ("preconditions", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v),
            "postconditions": ("postconditions", lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v),
            "compatible_adapters": ("compatible_adapters", lambda v: list(v)),
            "is_active": ("is_active", lambda v: bool(v)),
        }

        set_clauses = []
        set_params = []
        for k, val in updates.items():
            if k in field_mapping:
                col_name, transform = field_mapping[k]
                set_clauses.append(f"{col_name} = %s")
                set_params.append(transform(val))

        if not set_clauses:
            return existing

        set_clauses.append("updated_at = NOW()")
        sql = f"UPDATE algorithm_registry SET {', '.join(set_clauses)} WHERE id = %s RETURNING *"
        set_params.append(algo_id)

        try:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(set_params))
                row = cur.fetchone()
            conn.commit()
            if not row:
                return None
            return self._row_to_contract(row, cur.description)
        except Exception:
            conn.rollback()
            raise

    def delete_algorithm(self, algo_id: str, hard_delete: bool = False) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                if hard_delete:
                    cur.execute("DELETE FROM algorithm_registry WHERE id = %s", (algo_id,))
                else:
                    cur.execute("UPDATE algorithm_registry SET is_active = FALSE, updated_at = NOW() WHERE id = %s", (algo_id,))
                affected = cur.rowcount
            conn.commit()
            return affected > 0
        except Exception:
            conn.rollback()
            raise

    def register_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        return self.upsert_adapter(adapter)

    def upsert_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
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
                    RETURNING id, name, source_type, target_type, algo_id, is_lossy, description
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
                r = cur.fetchone()
            conn.commit()
            return TypeAdapterContract(
                id=r[0],
                name=r[1],
                source_type=r[2],
                target_type=r[3],
                algo_id=r[4],
                is_lossy=bool(r[5]),
                description=r[6],
            )
        except Exception:
            conn.rollback()
            raise

    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, source_type, target_type, algo_id, is_lossy, description FROM type_adapters WHERE source_type = %s AND target_type = %s",
                (source_type, target_type),
            )
            rows = cur.fetchall()
            return [
                TypeAdapterContract(
                    id=r[0],
                    name=r[1],
                    source_type=r[2],
                    target_type=r[3],
                    algo_id=r[4],
                    is_lossy=bool(r[5]),
                    description=r[6],
                )
                for r in rows
            ]

    def list_adapters(self) -> List[TypeAdapterContract]:
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, source_type, target_type, algo_id, is_lossy, description FROM type_adapters ORDER BY id ASC")
            rows = cur.fetchall()
            return [
                TypeAdapterContract(
                    id=r[0],
                    name=r[1],
                    source_type=r[2],
                    target_type=r[3],
                    algo_id=r[4],
                    is_lossy=bool(r[5]),
                    description=r[6],
                )
                for r in rows
            ]

    def delete_adapter(self, adapter_id: str) -> bool:
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM type_adapters WHERE id = %s", (adapter_id,))
                affected = cur.rowcount
            conn.commit()
            return affected > 0
        except Exception:
            conn.rollback()
            raise

    def _row_to_contract(self, row: tuple, description: Any) -> AlgorithmContract:
        col_names = [d[0] for d in description]
        data = dict(zip(col_names, row))

        input_schema = data["input_schema"] if isinstance(data["input_schema"], dict) else json.loads(data["input_schema"])
        output_schema = data["output_schema"] if isinstance(data["output_schema"], dict) else json.loads(data["output_schema"])
        params_schema = data["parameters_schema"] if isinstance(data["parameters_schema"], dict) else json.loads(data["parameters_schema"] or "{}")
        preconds = data["preconditions"] if isinstance(data["preconditions"], list) else json.loads(data["preconditions"] or "[]")
        postconds = data["postconditions"] if isinstance(data["postconditions"], list) else json.loads(data["postconditions"] or "[]")
        tags = data["capability_tags"] if isinstance(data["capability_tags"], list) else json.loads(data["capability_tags"] or "[]")
        adapters = data["compatible_adapters"] if isinstance(data["compatible_adapters"], list) else json.loads(data["compatible_adapters"] or "[]")

        return AlgorithmContract(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            category=AlgorithmCategory(data["category"]),
            capability_tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            parameters_schema=params_schema,
            purity=Purity(data["purity"]),
            determinism=Determinism(data["determinism"]),
            idempotency=Idempotency(data["idempotency"]),
            reversibility=Reversibility(data["reversibility"]),
            side_effects=SideEffectScope(data["side_effects"]),
            concurrency_model=ConcurrencyModel(data["concurrency_model"]),
            hardware_target=HardwareTarget(data["hardware_target"]),
            complexity=ComplexityCost(time=data["time_complexity"], space=data["space_complexity"]),
            preconditions=preconds,
            postconditions=postconds,
            compatible_adapters=adapters,
            is_active=bool(data["is_active"]),
        )


PostgresAlgorithmRegistryAdapter = AlloyDBAlgorithmRegistryAdapter
