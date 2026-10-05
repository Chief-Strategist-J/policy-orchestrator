"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNIT TESTS FOR ALGORITHM REGISTRY CRUD & REST API
================================================================================

1. OVERVIEW & OBJECTIVE:
   Tests complete CRUD lifecycle (Upsert, Read, Filter, Update, Soft/Hard Delete),
   seed synchronization, contract parity checks, and REST API V1 endpoints
   for database-backed algorithm catalog storage.
================================================================================
"""

import pytest
from fastapi.testclient import TestClient

from src.api.rest.app import app
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
from src.infra.adapters.database import (
    SQLiteAlgorithmRegistryAdapter,
    InMemoryAlgorithmRegistryAdapter,
)
from src.features.code_engine.service.algorithm_registry_service import AlgorithmRegistryService
from src.features.code_engine.registry.algorithm_catalog import BUILTIN_ALGORITHM_CONTRACTS


@pytest.fixture
def sqlite_service(tmp_path):
    db_file = tmp_path / "crud_test.db"
    adapter = SQLiteAlgorithmRegistryAdapter(str(db_file), auto_migrate=True)
    return AlgorithmRegistryService(adapter)


@pytest.fixture
def memory_service():
    adapter = InMemoryAlgorithmRegistryAdapter(load_builtins=True)
    return AlgorithmRegistryService(adapter)


def test_sqlite_algorithm_crud_lifecycle(sqlite_service):
    # 1. Verify initial seeded count
    all_algos = sqlite_service.list_algorithms()
    assert len(all_algos) == 242

    # 2. Get specific algorithm
    search_01 = sqlite_service.get_algorithm("ALGO-SRCH-01")
    assert search_01 is not None
    assert search_01.name == "SearchEngineRecursiveWalkAlgo"
    assert search_01.category == AlgorithmCategory.SEARCH

    # 3. Create (Upsert) new custom algorithm
    custom_contract = AlgorithmContract(
        id="ALGO-CUSTOM-999",
        name="CustomTestAlgo",
        version="1.0.0",
        category=AlgorithmCategory.SEARCH,
        capability_tags=["custom.test", "search.fast"],
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        purity=Purity.PURE,
        determinism=Determinism.DETERMINISTIC,
        idempotency=Idempotency.IDEMPOTENT,
        reversibility=Reversibility.REVERSIBLE,
        side_effects=SideEffectScope.READ_ONLY,
        complexity=ComplexityCost(time="O(1)", space="O(1)"),
    )
    saved = sqlite_service.upsert_algorithm(custom_contract)
    assert saved.id == "ALGO-CUSTOM-999"

    fetched = sqlite_service.get_algorithm("ALGO-CUSTOM-999")
    assert fetched is not None
    assert fetched.name == "CustomTestAlgo"

    # 4. Upsert existing (Update on conflict)
    updated_custom = AlgorithmContract(
        id="ALGO-CUSTOM-999",
        name="CustomTestAlgoUpdated",
        version="2.0.0",
        category=AlgorithmCategory.SEARCH,
        capability_tags=["custom.test", "search.ultra_fast"],
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        purity=Purity.PURE,
        determinism=Determinism.DETERMINISTIC,
        idempotency=Idempotency.IDEMPOTENT,
        reversibility=Reversibility.REVERSIBLE,
        side_effects=SideEffectScope.READ_ONLY,
        complexity=ComplexityCost(time="O(log N)", space="O(1)"),
    )
    sqlite_service.upsert_algorithm(updated_custom)
    fetched2 = sqlite_service.get_algorithm("ALGO-CUSTOM-999")
    assert fetched2 is not None
    assert fetched2.name == "CustomTestAlgoUpdated"
    assert fetched2.version == "2.0.0"

    # 5. Partial Update
    sqlite_service.update_algorithm("ALGO-CUSTOM-999", {"name": "CustomTestAlgoPatched", "time_complexity": "O(N)"})
    fetched3 = sqlite_service.get_algorithm("ALGO-CUSTOM-999")
    assert fetched3 is not None
    assert fetched3.name == "CustomTestAlgoPatched"
    assert fetched3.complexity.time == "O(N)"

    # 6. Filter by Tag & Category
    tagged = sqlite_service.list_algorithms(tags=["custom.test"])
    assert len(tagged) == 1
    assert tagged[0].id == "ALGO-CUSTOM-999"

    # 7. Soft Delete
    deleted = sqlite_service.delete_algorithm("ALGO-CUSTOM-999", hard_delete=False)
    assert deleted is True
    assert sqlite_service.get_algorithm("ALGO-CUSTOM-999").is_active is False
    assert len(sqlite_service.list_algorithms(tags=["custom.test"], is_active=True)) == 0
    assert len(sqlite_service.list_algorithms(tags=["custom.test"], is_active=False)) == 1

    # 8. Hard Delete
    hard_deleted = sqlite_service.delete_algorithm("ALGO-CUSTOM-999", hard_delete=True)
    assert hard_deleted is True
    assert sqlite_service.get_algorithm("ALGO-CUSTOM-999") is None


def test_sqlite_type_adapter_crud(sqlite_service):
    # 1. Initial seeded adapters
    adapters = sqlite_service.list_adapters()
    assert len(adapters) == 11

    # 2. Upsert new adapter
    custom_adapter = TypeAdapterContract(
        id="ADAPT-TEST-01",
        name="CustomTextToTokensAdapter",
        source_type="text/plain",
        target_type="tokens/array",
        algo_id="ALGO-VEC-TRFM-01",
        is_lossy=False,
        description="Converts raw text to token sequence",
    )
    sqlite_service.upsert_adapter(custom_adapter)

    fetched = sqlite_service.get_adapters_for_types("text/plain", "tokens/array")
    assert len(fetched) == 1
    assert fetched[0].id == "ADAPT-TEST-01"

    # 3. Delete adapter
    del_res = sqlite_service.delete_adapter("ADAPT-TEST-01")
    assert del_res is True
    assert len(sqlite_service.get_adapters_for_types("text/plain", "tokens/array")) == 0


def test_parity_verification(sqlite_service, memory_service):
    # Test SQLite parity
    parity_sqlite = sqlite_service.verify_parity_with_builtins()
    assert parity_sqlite["is_exact_parity"] is True
    assert parity_sqlite["code_count"] == 242
    assert parity_sqlite["db_count"] == 242
    assert len(parity_sqlite["missing_ids"]) == 0
    assert len(parity_sqlite["extra_ids"]) == 0
    assert len(parity_sqlite["mismatched_ids"]) == 0

    # Test InMemory parity
    parity_mem = memory_service.verify_parity_with_builtins()
    assert parity_mem["is_exact_parity"] is True
    assert parity_mem["code_count"] == 242
    assert parity_mem["db_count"] == 242


def test_rest_api_algorithm_registry_endpoints():
    client = TestClient(app)

    # 1. GET list contracts
    res = client.get("/api/v1/algorithms/registry/contracts")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert len(body["data"]) >= 242

    # 2. GET single contract
    res_single = client.get("/api/v1/algorithms/registry/contracts/ALGO-SRCH-01")
    assert res_single.status_code == 200
    body_single = res_single.json()
    assert body_single["success"] is True
    assert body_single["data"]["id"] == "ALGO-SRCH-01"
    assert body_single["data"]["name"] == "SearchEngineRecursiveWalkAlgo"

    # 3. POST upsert contract
    upsert_payload = {
        "id": "ALGO-API-TEST-01",
        "name": "ApiTestAlgorithm",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["api.test"],
        "input_schema": {"type": "object"},
        "output_schema": {"type": "object"},
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "REVERSIBLE",
        "side_effects": "READ_ONLY",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "is_active": True,
    }

    try:
        res_post = client.post("/api/v1/algorithms/registry/contracts", json=upsert_payload)
        assert res_post.status_code == 200
        assert res_post.json()["data"]["id"] == "ALGO-API-TEST-01"

        # 4. PATCH contract
        res_patch = client.patch(
            "/api/v1/algorithms/registry/contracts/ALGO-API-TEST-01",
            json={"name": "ApiTestAlgorithmUpdated", "time_complexity": "O(N)"},
        )
        assert res_patch.status_code == 200
        assert res_patch.json()["data"]["name"] == "ApiTestAlgorithmUpdated"
        assert res_patch.json()["data"]["complexity"]["time"] == "O(N)"
    finally:
        # Cleanup
        client.delete("/api/v1/algorithms/registry/contracts/ALGO-API-TEST-01?hard_delete=true")

    # 5. POST Seed
    res_seed = client.post("/api/v1/algorithms/registry/seed")
    assert res_seed.status_code == 200
    assert res_seed.json()["data"]["seeded_algorithms"] == 242

    # 6. GET Parity check
    res_parity = client.get("/api/v1/algorithms/registry/parity")
    assert res_parity.status_code == 200
    assert res_parity.json()["data"]["code_count"] == 242
    assert res_parity.json()["data"]["is_exact_parity"] is True

