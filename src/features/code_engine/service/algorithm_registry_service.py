"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ALGORITHM REGISTRY & SEEDER SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Domain service managing Layer 1 Algorithm Contracts and Type Adapters in the
   database (Google AlloyDB Omni, PostgreSQL, SQLite, or In-Memory).
   Provides strict CRUD operations, deterministic Upsert behavior, and catalog
   parity verification against in-code specifications.

2. ARCHITECTURAL LOCATION:
   src/features/code_engine/service/algorithm_registry_service.py
   Adheres to api.structure.working.rule.md Section 3.8.
================================================================================
"""

from typing import List, Optional, Dict, Any
from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    TypeAdapterContract,
    AlgorithmCategory,
    Purity,
    SideEffectScope,
)
from src.domain.ports.algorithm_registry_port import AlgorithmRegistryPort
from src.features.code_engine.registry.algorithm_catalog import (
    BUILTIN_ALGORITHM_CONTRACTS,
    BUILTIN_TYPE_ADAPTERS,
)


class AlgorithmRegistryService:
    def __init__(self, registry_adapter: AlgorithmRegistryPort) -> None:
        self.registry = registry_adapter

    def get_algorithm(self, algo_id: str) -> Optional[AlgorithmContract]:
        return self.registry.get_algorithm(algo_id)

    def list_algorithms(
        self,
        category: Optional[AlgorithmCategory] = None,
        tags: Optional[List[str]] = None,
        purity: Optional[Purity] = None,
        side_effects: Optional[SideEffectScope] = None,
        is_active: bool = True,
    ) -> List[AlgorithmContract]:
        return self.registry.list_algorithms(
            category=category,
            tags=tags,
            purity=purity,
            side_effects=side_effects,
            is_active=is_active,
        )

    def upsert_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        return self.registry.upsert_algorithm(contract)

    def update_algorithm(self, algo_id: str, updates: Dict[str, Any]) -> Optional[AlgorithmContract]:
        return self.registry.update_algorithm(algo_id, updates)

    def delete_algorithm(self, algo_id: str, hard_delete: bool = False) -> bool:
        return self.registry.delete_algorithm(algo_id, hard_delete=hard_delete)

    def list_adapters(self) -> List[TypeAdapterContract]:
        return self.registry.list_adapters()

    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        return self.registry.get_adapters_for_types(source_type, target_type)

    def upsert_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        return self.registry.upsert_adapter(adapter)

    def delete_adapter(self, adapter_id: str) -> bool:
        return self.registry.delete_adapter(adapter_id)

    def seed_all_builtins(self) -> Dict[str, int]:
        algo_count = 0
        adapter_count = 0

        for contract in BUILTIN_ALGORITHM_CONTRACTS:
            self.registry.upsert_algorithm(contract)
            algo_count += 1

        for adapter in BUILTIN_TYPE_ADAPTERS:
            self.registry.upsert_adapter(adapter)
            adapter_count += 1

        return {
            "seeded_algorithms": algo_count,
            "seeded_adapters": adapter_count,
        }

    def verify_parity_with_builtins(self) -> Dict[str, Any]:
        db_algos = {a.id: a for a in self.registry.list_algorithms(is_active=True)}
        code_algos = {a.id: a for a in BUILTIN_ALGORITHM_CONTRACTS if a.is_active}

        missing = [aid for aid in code_algos if aid not in db_algos]
        extra = [aid for aid in db_algos if aid not in code_algos]
        mismatches = []

        for aid, code_algo in code_algos.items():
            if aid in db_algos:
                db_algo = db_algos[aid]
                if (
                    code_algo.name != db_algo.name
                    or code_algo.version != db_algo.version
                    or code_algo.category != db_algo.category
                    or code_algo.complexity.time != db_algo.complexity.time
                    or code_algo.complexity.space != db_algo.complexity.space
                    or code_algo.purity != db_algo.purity
                    or code_algo.determinism != db_algo.determinism
                    or code_algo.idempotency != db_algo.idempotency
                    or code_algo.side_effects != db_algo.side_effects
                ):
                    mismatches.append(aid)

        return {
            "is_exact_parity": len(missing) == 0 and len(extra) == 0 and len(mismatches) == 0,
            "code_count": len(code_algos),
            "db_count": len(db_algos),
            "missing_ids": missing,
            "extra_ids": extra,
            "mismatched_ids": mismatches,
        }
