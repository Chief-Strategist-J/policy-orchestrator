"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CODE ENGINE ALGORITHM CATALOG
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides declarative Layer 1 (G1-G6) contract definitions for all 242
   Search, Observability, Update, Vector, and Graph algorithms, and G4 Type Adapters.
   Data is persisted in database/migrations/ and loaded from canonical database seeds.

2. ARCHITECTURAL LOCATION:
   src/features/code_engine/registry/algorithm_catalog.py
   Adheres to api.structure.working.rule.md Section 3.8 and database migration doctrine.
================================================================================
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    AlgorithmCategory,
    Purity,
    Determinism,
    Idempotency,
    Reversibility,
    SideEffectScope,
    ConcurrencyModel,
    HardwareTarget,
    ComplexityCost,
    TypeAdapterContract,
)


def _load_catalog_definitions() -> tuple[List[AlgorithmContract], List[TypeAdapterContract]]:
    json_path = Path(__file__).resolve().parents[4] / "database" / "seeds" / "algorithm_catalog.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Algorithm catalog seed file missing at: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))

    algorithms: List[AlgorithmContract] = []
    for item in data.get("algorithms", []):
        contract = AlgorithmContract(
            id=item["id"],
            name=item["name"],
            version=item.get("version", "1.0.0"),
            category=AlgorithmCategory(item["category"]),
            capability_tags=item.get("capability_tags", []),
            input_schema=item["input_schema"],
            output_schema=item["output_schema"],
            parameters_schema=item.get("parameters_schema", {}),
            purity=Purity(item["purity"]),
            determinism=Determinism(item["determinism"]),
            idempotency=Idempotency(item["idempotency"]),
            reversibility=Reversibility(item["reversibility"]),
            side_effects=SideEffectScope(item["side_effects"]),
            concurrency_model=ConcurrencyModel(item.get("concurrency_model", "THREAD_SAFE")),
            hardware_target=HardwareTarget(item.get("hardware_target", "CPU_SCALAR")),
            complexity=ComplexityCost(
                time=item.get("time_complexity", "O(N)"),
                space=item.get("space_complexity", "O(1)"),
            ),
            preconditions=item.get("preconditions", []),
            postconditions=item.get("postconditions", []),
            compatible_adapters=item.get("compatible_adapters", []),
            is_active=item.get("is_active", True),
        )
        algorithms.append(contract)

    adapters: List[TypeAdapterContract] = []
    for a in data.get("type_adapters", []):
        adapter = TypeAdapterContract(
            id=a["id"],
            name=a["name"],
            source_type=a["source_type"],
            target_type=a["target_type"],
            algo_id=a.get("algo_id"),
            is_lossy=a.get("is_lossy", False),
            description=a.get("description", ""),
        )
        adapters.append(adapter)

    return algorithms, adapters


BUILTIN_ALGORITHM_CONTRACTS: List[AlgorithmContract]
BUILTIN_TYPE_ADAPTERS: List[TypeAdapterContract]

BUILTIN_ALGORITHM_CONTRACTS, BUILTIN_TYPE_ADAPTERS = _load_catalog_definitions()


def get_builtin_algorithm(algo_id: str) -> Optional[AlgorithmContract]:
    for a in BUILTIN_ALGORITHM_CONTRACTS:
        if a.id == algo_id:
            return a
    return None


def get_builtin_adapter(adapter_id: str) -> Optional[TypeAdapterContract]:
    for a in BUILTIN_TYPE_ADAPTERS:
        if a.id == adapter_id:
            return a
    return None
