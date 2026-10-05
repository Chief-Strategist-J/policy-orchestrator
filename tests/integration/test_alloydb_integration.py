"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ALLOYDB OMNI / POSTGRESQL INTEGRATION TEST
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates end-to-end database connectivity, schema migration execution,
   GIN-indexed JSONB query resolution, and pipeline DAG composition against
   a live Google AlloyDB Omni / PostgreSQL 15+ instance.
================================================================================
"""

import os
import pytest
from src.infra.adapters.database import (
    DatabaseMigrationRunner,
    AlloyDBAlgorithmRegistryAdapter,
    PostgresAlgorithmRegistryAdapter,
)


from src.features.code_engine.service.algorithm_composer_service import AlgorithmComposerService
from src.domain.models.algorithm_contract import AlgorithmCategory

ALLOYDB_TEST_URL = os.environ.get(
    "ALLOYDB_TEST_URL",
    "postgresql://alloy_admin:alloysecret@127.0.0.1:5432/policy_orchestration",
)



def _is_alloydb_reachable() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(ALLOYDB_TEST_URL, connect_timeout=2)
        conn.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _is_alloydb_reachable(), reason="Live AlloyDB / PostgreSQL is not reachable on localhost:5432")
class TestAlloyDBIntegration:
    def test_live_alloydb_migration_and_seeding(self):
        runner = DatabaseMigrationRunner(ALLOYDB_TEST_URL)
        runner.run_migrations()
        count = runner.seed_algorithm_catalog()
        assert count == 24

    def test_live_alloydb_adapter_queries_and_gin_index(self):
        adapter = AlloyDBAlgorithmRegistryAdapter(ALLOYDB_TEST_URL)
        all_algos = adapter.list_algorithms()
        assert len(all_algos) == 24

        # Test GIN index query for capability tag
        multipattern_algos = adapter.list_algorithms(tags=["search.multipattern"])
        assert len(multipattern_algos) >= 1
        assert multipattern_algos[0].id == "ALGO-SRCH-11"
        assert multipattern_algos[0].name == "SearchEngineAhoCorasickAlgo"

        # Test Category filtering
        search_algos = adapter.list_algorithms(category=AlgorithmCategory.SEARCH)
        assert len(search_algos) == 15

        obs_algos = adapter.list_algorithms(category=AlgorithmCategory.OBSERVABILITY)
        assert len(obs_algos) == 6

        upd_algos = adapter.list_algorithms(category=AlgorithmCategory.UPDATE)
        assert len(upd_algos) == 3

    def test_live_alloydb_type_adapters_and_composition(self):
        adapter = PostgresAlgorithmRegistryAdapter(ALLOYDB_TEST_URL)
        adapters = adapter.list_adapters()
        assert len(adapters) == 5

        composer = AlgorithmComposerService(adapter)
        pipeline = composer.compose_pipeline(["ALGO-SRCH-01", "ALGO-OBS-17", "ALGO-OBS-18"])
        assert pipeline["is_valid"] is True
        assert pipeline["total_steps"] == 3
