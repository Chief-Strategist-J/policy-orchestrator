"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IN-MEMORY ALGORITHM REGISTRY ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   In-memory implementation of AlgorithmRegistryPort with full CRUD,
   upsert semantics, GIN-style tag matching, and property filtering for fast
   local testing, offline execution, and fallback resilience.

2. ARCHITECTURAL LOCATION:
   src/infra/adapters/database/in_memory_algorithm_registry_adapter.py
   Adheres to api.structure.working.rule.md Section 3.8.
================================================================================
"""

from typing import Dict, List, Optional, Any
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


class InMemoryAlgorithmRegistryAdapter(AlgorithmRegistryPort):
    def __init__(self, load_builtins: bool = True) -> None:
        self._algorithms: Dict[str, AlgorithmContract] = {}
        self._adapters: Dict[str, TypeAdapterContract] = {}

        if load_builtins:
            for algo in BUILTIN_ALGORITHM_CONTRACTS:
                self.register_algorithm(algo)
            for adapter in BUILTIN_TYPE_ADAPTERS:
                self.register_adapter(adapter)

    def register_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        return self.upsert_algorithm(contract)

    def upsert_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        self._algorithms[contract.id] = contract
        return contract

    def get_algorithm(self, algo_id: str) -> Optional[AlgorithmContract]:
        return self._algorithms.get(algo_id)

    def list_algorithms(
        self,
        category: Optional[AlgorithmCategory] = None,
        tags: Optional[List[str]] = None,
        purity: Optional[Purity] = None,
        side_effects: Optional[SideEffectScope] = None,
        is_active: bool = True,
    ) -> List[AlgorithmContract]:
        results: List[AlgorithmContract] = []
        for algo in sorted(self._algorithms.values(), key=lambda a: a.id):
            if algo.is_active != is_active:
                continue
            if category and algo.category != category:
                continue
            if purity and algo.purity != purity:
                continue
            if side_effects and algo.side_effects != side_effects:
                continue
            if tags:
                if not all(t in algo.capability_tags for t in tags):
                    continue
            results.append(algo)
        return results

    def update_algorithm(self, algo_id: str, updates: Dict[str, Any]) -> Optional[AlgorithmContract]:
        if algo_id not in self._algorithms:
            return None
        existing = self._algorithms[algo_id]
        data = existing.model_dump() if hasattr(existing, "model_dump") else existing.dict()
        updates_copy = dict(updates)
        if "time_complexity" in updates_copy or "space_complexity" in updates_copy:
            time_c = updates_copy.pop("time_complexity", existing.complexity.time)
            space_c = updates_copy.pop("space_complexity", existing.complexity.space)
            data["complexity"] = {"time": time_c, "space": space_c}
        data.update(updates_copy)
        updated = AlgorithmContract(**data)
        self._algorithms[algo_id] = updated
        return updated

    def delete_algorithm(self, algo_id: str, hard_delete: bool = False) -> bool:
        if algo_id not in self._algorithms:
            return False
        if hard_delete:
            del self._algorithms[algo_id]
        else:
            self._algorithms[algo_id].is_active = False
        return True

    def register_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        return self.upsert_adapter(adapter)

    def upsert_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        self._adapters[adapter.id] = adapter
        return adapter

    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        return [
            a for a in self._adapters.values()
            if a.source_type == source_type and a.target_type == target_type
        ]

    def list_adapters(self) -> List[TypeAdapterContract]:
        return sorted(list(self._adapters.values()), key=lambda a: a.id)

    def delete_adapter(self, adapter_id: str) -> bool:
        if adapter_id not in self._adapters:
            return False
        del self._adapters[adapter_id]
        return True
