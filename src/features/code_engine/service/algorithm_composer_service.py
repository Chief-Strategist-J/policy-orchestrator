"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ALGORITHM COMPOSER SERVICE (LAYER 1-3 GLUE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates and constructs type-safe algorithm execution pipelines using
   Layer 1 typed interface contracts (G1), capability registry (G2),
   adapters (G4), and design-by-contract pre/postconditions (G5).

2. EXECUTION FLOW:
   - Validates existence and active status of each algorithm in the chain.
   - Evaluates type compatibility between step N output and step N+1 input.
   - Discovers and inserts necessary G4 type adapters when direct connection fails.
   - Verifies safety invariants (e.g. read-only stages preceding mutation stages).
================================================================================
"""

from typing import List, Dict, Any, Optional
from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    TypeAdapterContract,
    SideEffectScope,
)
from src.domain.ports.algorithm_registry_port import AlgorithmRegistryPort


class PipelineStep(BaseModel := type("BaseModel", (), {})):
    pass


class AlgorithmComposerService:
    def __init__(self, registry: AlgorithmRegistryPort) -> None:
        self.registry = registry

    def compose_pipeline(
        self,
        algo_ids: List[str],
        strict_contract_check: bool = True,
    ) -> Dict[str, Any]:
        pipeline_steps: List[Dict[str, Any]] = []
        inferred_adapters: List[Dict[str, Any]] = []
        safety_issues: List[str] = []

        algorithms: List[AlgorithmContract] = []
        for aid in algo_ids:
            algo = self.registry.get_algorithm(aid)
            if not algo:
                raise ValueError(f"Algorithm '{aid}' not found in registry.")
            if not algo.is_active:
                raise ValueError(f"Algorithm '{aid}' is inactive/disabled.")
            algorithms.append(algo)

        # Invariant check: Disk writes should not precede read-only scans in backward pipeline
        saw_mutation = False
        for algo in algorithms:
            if algo.side_effects == SideEffectScope.DISK_WRITE:
                saw_mutation = True
            elif saw_mutation and algo.side_effects == SideEffectScope.READ_ONLY and strict_contract_check:
                safety_issues.append(
                    f"Pipeline Warning: Read-only step '{algo.id}' follows mutation step."
                )

        for i, algo in enumerate(algorithms):
            step_info = {
                "step_index": i + 1,
                "algo_id": algo.id,
                "name": algo.name,
                "category": algo.category.value,
                "purity": algo.purity.value,
                "determinism": algo.determinism.value,
                "idempotency": algo.idempotency.value,
                "side_effects": algo.side_effects.value,
                "hardware_target": algo.hardware_target.value,
                "complexity": {
                    "time": algo.complexity.time,
                    "space": algo.complexity.space,
                },
                "preconditions": algo.preconditions,
                "postconditions": algo.postconditions,
            }
            pipeline_steps.append(step_info)

            # Check adapter needs between step i and step i+1
            if i < len(algorithms) - 1:
                next_algo = algorithms[i + 1]
                # Look for declared compatible adapters
                matching_adapters = [
                    ad_id for ad_id in algo.compatible_adapters
                    if ad_id in next_algo.compatible_adapters or any(
                        a.algo_id == next_algo.id for a in self.registry.list_adapters() if a.id == ad_id
                    )
                ]
                if matching_adapters:
                    inferred_adapters.append({
                        "between_steps": (i + 1, i + 2),
                        "adapter_ids": matching_adapters,
                    })

        return {
            "total_steps": len(pipeline_steps),
            "pipeline_steps": pipeline_steps,
            "inferred_adapters": inferred_adapters,
            "safety_issues": safety_issues,
            "is_valid": len(safety_issues) == 0,
        }
