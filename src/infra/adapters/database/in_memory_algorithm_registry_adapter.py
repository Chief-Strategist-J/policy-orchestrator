"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IN-MEMORY ALGORITHM REGISTRY ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   In-memory implementation of AlgorithmRegistryPort with full GIN-style tag
   matching and property filtering for fast local testing and fallbacks.

2. ARCHITECTURAL LOCATION:
   src/infra/database/adapters/in_memory_algorithm_registry_adapter.py
   Adheres to api.structure.working.rule.md Section 3.8.
================================================================================
"""

from typing import Dict, List, Optional
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

    def register_algorithm(self, contract: AlgorithmContract) -> None:
        self._algorithms[contract.id] = contract

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
        for algo in self._algorithms.values():
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

    def register_adapter(self, adapter: TypeAdapterContract) -> None:
        self._adapters[adapter.id] = adapter

    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        return [
            a for a in self._adapters.values()
            if a.source_type == source_type and a.target_type == target_type
        ]

    def list_adapters(self) -> List[TypeAdapterContract]:
        return list(self._adapters.values())
