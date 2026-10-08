"""
================================================================================
UNIT TESTS: UPSTREAM & DOWNSTREAM IMPACT ANALYSIS SERVICE
================================================================================
"""

import pytest
from src.infra.adapters.graph.in_memory_graph_adapter import InMemoryGraphAdapter
from src.features.file_structure.service.file_structure_impact_analyzer_service import FileStructureImpactAnalyzerService
from src.features.file_structure.service.file_structure_graph_sync_service import FileStructureGraphSyncService
from src.features.file_structure.types.file_structure_types import (
    RISK_LEVEL_LEVEL_0,
    RISK_LEVEL_LEVEL_2,
    RISK_LEVEL_LEVEL_3,
)

@pytest.fixture
def impact_service():
    adapter = InMemoryGraphAdapter()
    sync_service = FileStructureGraphSyncService(graph_store=adapter)
    sync_service.sync_feature_dag("organizations")
    service = FileStructureImpactAnalyzerService(graph_store=adapter)
    return service

def test_upstream_impact_from_queries(impact_service):
    report = impact_service.analyze_upstream_impact("query_organizations_sql")
    
    assert report.direction == "UPSTREAM"
    assert report.target_id == "query_organizations_sql"
    assert len(report.impacted_nodes) > 0
    
    impacted_labels = {n.label for n in report.impacted_nodes}
    assert "RepositoryAdapter" in impacted_labels or "DomainService" in impacted_labels
    assert len(report.required_verification_commands) > 0

def test_downstream_impact_from_contract(impact_service):
    report = impact_service.analyze_downstream_impact("contract_openapi_organizations")
    
    assert report.direction == "DOWNSTREAM"
    assert report.target_id == "contract_openapi_organizations"
    
    impacted_labels = {n.label for n in report.impacted_nodes}
    assert "IngressRouter" in impacted_labels or "IngressHandler" in impacted_labels
    assert report.blast_radius_score >= 0

def test_isolated_rule_change_blast_radius(impact_service):
    report = impact_service.analyze_upstream_impact("rules_organizations")
    assert report.direction == "UPSTREAM"
    assert len(report.required_verification_commands) > 0

def test_empty_target_raises_error(impact_service):
    with pytest.raises(ValueError, match="target_id must not be empty"):
        impact_service.analyze_upstream_impact("")

def test_scan_and_index_repository(tmp_path):
    adapter = InMemoryGraphAdapter()
    sync_service = FileStructureGraphSyncService(graph_store=adapter)
    impact_service = FileStructureImpactAnalyzerService(graph_store=adapter)
    
    feat_dir = tmp_path / "src" / "features" / "billing" / "queries"
    feat_dir.mkdir(parents=True)
    (feat_dir / "billing.queries.sql").write_text("-- name: FLOW_GET_BILLING", encoding="utf-8")
    
    res = sync_service.scan_and_index_repository(str(tmp_path))
    assert res["indexed_files"] >= 1
    assert res["status"] == "COMPLETED"

def test_link_shared_dependency():
    from src.features.file_structure.service.file_structure_service import FileStructureDomainService
    adapter = InMemoryGraphAdapter()
    service = FileStructureDomainService(graph_store=adapter)
    service.graph_sync.sync_feature_dag("organizations")
    service.link_shared(feature_name="organizations", shared_file="src/shared/utils/formatters.py")
    
    assert "shared_formatters" in adapter._nodes
    assert adapter._nodes["shared_formatters"].label == "SharedLibrary"

