"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNIT TESTS FOR REGISTRY & COMPOSER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests registry queries, property filtering, and dynamic pipeline composition
   with G4 adapter inference.
================================================================================
"""

import pytest
from src.domain.models.algorithm_contract import (
    AlgorithmCategory,
    Purity,
    SideEffectScope,
)
from src.infra.adapters.database import (
    SQLiteAlgorithmRegistryAdapter,
    InMemoryAlgorithmRegistryAdapter,
)

from src.features.code_engine.service.algorithm_composer_service import AlgorithmComposerService


@pytest.fixture
def sqlite_registry(tmp_path):
    db_file = tmp_path / "reg_test.db"
    return SQLiteAlgorithmRegistryAdapter(str(db_file), auto_migrate=True)


@pytest.fixture
def in_memory_registry():
    return InMemoryAlgorithmRegistryAdapter(load_builtins=True)


def test_registry_fetch_and_filtering(sqlite_registry):
    # Fetch by ID
    ac = sqlite_registry.get_algorithm("ALGO-SRCH-11")
    assert ac is not None
    assert ac.name == "SearchEngineAhoCorasickAlgo"
    assert ac.category == AlgorithmCategory.SEARCH
    assert ac.purity == Purity.PURE

    # Filter by category
    obs_algos = sqlite_registry.list_algorithms(category=AlgorithmCategory.OBSERVABILITY)
    assert len(obs_algos) == 51

    # Filter by capability tags
    multipattern = sqlite_registry.list_algorithms(tags=["search.multipattern"])
    assert len(multipattern) >= 1
    assert any(m.id == "ALGO-SRCH-11" for m in multipattern)

    # Filter by side effects
    disk_writers = sqlite_registry.list_algorithms(side_effects=SideEffectScope.DISK_WRITE)
    assert len(disk_writers) == 1
    assert disk_writers[0].id == "ALGO-UPD-23"


def test_composer_pipeline_generation(sqlite_registry):
    composer = AlgorithmComposerService(sqlite_registry)

    # Valid pipeline: Git Walk -> Aho Corasick -> Position Span Tracker -> Atomic Patcher
    pipeline = ["ALGO-SRCH-03", "ALGO-SRCH-11", "ALGO-OBS-16", "ALGO-UPD-23"]
    plan = composer.compose_pipeline(pipeline)

    assert plan["is_valid"] is True
    assert plan["total_steps"] == 4
    assert len(plan["pipeline_steps"]) == 4
    assert len(plan["inferred_adapters"]) >= 1


def test_composer_safety_warning(sqlite_registry):
    composer = AlgorithmComposerService(sqlite_registry)

    # Dangerous backward pipeline: Write to disk before reading
    pipeline = ["ALGO-UPD-23", "ALGO-SRCH-01"]
    plan = composer.compose_pipeline(pipeline, strict_contract_check=True)

    assert plan["is_valid"] is False
    assert len(plan["safety_issues"]) > 0
    assert "Read-only step" in plan["safety_issues"][0]


def test_in_memory_registry_parity(in_memory_registry):
    ac = in_memory_registry.get_algorithm("ALGO-UPD-22")
    assert ac is not None
    assert ac.name == "CstMatcher"

    adapters = in_memory_registry.list_adapters()
    assert len(adapters) >= 5
