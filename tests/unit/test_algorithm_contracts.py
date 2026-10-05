"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNIT TESTS FOR ALGORITHM CONTRACTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates that all 24 built-in Search, Observability, and Update algorithms
   possess complete, compliant Layer 1 (G1-G6) contracts with all 16 properties.
================================================================================
"""

import pytest
from src.domain.models.algorithm_contract import (
    AlgorithmCategory,
    Purity,
    Determinism,
    Idempotency,
    Reversibility,
    SideEffectScope,
    ConcurrencyModel,
    HardwareTarget,
)
from src.features.code_engine.registry.algorithm_catalog import (
    BUILTIN_ALGORITHM_CONTRACTS,
    BUILTIN_TYPE_ADAPTERS,
)


def test_builtin_algorithms_count_and_uniqueness():
    assert len(BUILTIN_ALGORITHM_CONTRACTS) == 33
    ids = [algo.id for algo in BUILTIN_ALGORITHM_CONTRACTS]
    assert len(set(ids)) == 33, "All algorithm IDs must be unique"


def test_all_algorithms_have_all_16_properties():
    for algo in BUILTIN_ALGORITHM_CONTRACTS:
        assert algo.id.startswith("ALGO-")
        assert len(algo.name) > 0
        assert len(algo.version) > 0
        assert isinstance(algo.category, AlgorithmCategory)
        assert len(algo.capability_tags) > 0
        assert isinstance(algo.input_schema, dict) and "type" in algo.input_schema
        assert isinstance(algo.output_schema, dict) and "type" in algo.output_schema
        assert isinstance(algo.parameters_schema, dict)
        assert isinstance(algo.purity, Purity)
        assert isinstance(algo.determinism, Determinism)
        assert isinstance(algo.idempotency, Idempotency)
        assert isinstance(algo.reversibility, Reversibility)
        assert isinstance(algo.side_effects, SideEffectScope)
        assert isinstance(algo.concurrency_model, ConcurrencyModel)
        assert isinstance(algo.hardware_target, HardwareTarget)
        assert len(algo.complexity.time) > 0
        assert len(algo.complexity.space) > 0
        assert isinstance(algo.preconditions, list)
        assert isinstance(algo.postconditions, list)
        assert isinstance(algo.compatible_adapters, list)
        assert isinstance(algo.is_active, bool)


def test_category_distribution():
    search_algos = [a for a in BUILTIN_ALGORITHM_CONTRACTS if a.category == AlgorithmCategory.SEARCH]
    obs_algos = [a for a in BUILTIN_ALGORITHM_CONTRACTS if a.category == AlgorithmCategory.OBSERVABILITY]
    update_algos = [a for a in BUILTIN_ALGORITHM_CONTRACTS if a.category == AlgorithmCategory.UPDATE]
    vector_algos = [a for a in BUILTIN_ALGORITHM_CONTRACTS if a.category == AlgorithmCategory.VECTOR]

    assert len(search_algos) == 15
    assert len(obs_algos) == 6
    assert len(update_algos) == 3
    assert len(vector_algos) == 9


def test_type_adapters_catalog():
    assert len(BUILTIN_TYPE_ADAPTERS) == 11
    adapter_ids = [a.id for a in BUILTIN_TYPE_ADAPTERS]
    assert len(set(adapter_ids)) == len(BUILTIN_TYPE_ADAPTERS)
    for adapter in BUILTIN_TYPE_ADAPTERS:
        assert len(adapter.source_type) > 0
        assert len(adapter.target_type) > 0
