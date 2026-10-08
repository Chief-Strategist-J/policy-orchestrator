"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE FEATURE PUBLIC FACADE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Public facade entry point for the File Structure feature.
   Exports domain services, schemas, and public DTOs.
   Never leaks internal SQL queries or concrete database adapters.
================================================================================
"""

from src.features.file_structure.service.file_structure_service import (
    FileStructureDomainService,
    FileStructureService,
    KnowledgeGraphDomainService,
)
from src.features.file_structure.service.file_structure_scaffolder_service import FileStructureScaffolderService
from src.features.file_structure.service.file_structure_graph_sync_service import FileStructureGraphSyncService
from src.features.file_structure.service.file_structure_impact_analyzer_service import FileStructureImpactAnalyzerService
from src.features.file_structure.service.file_structure_map_resolver_service import FileStructureMapResolverService
from src.domain.ports.impact_analysis_port import ImpactAnalysisReportModel, ImpactedNodeModel
from src.features.file_structure.schema.file_structure_schema import (
    FileStructureEntitySchema,
    KnowledgeGraphEntitySchema,
    ScaffoldFeatureRequestSchema,
    ScaffoldPackageRequestSchema,
    AnalyzeImpactRequestSchema,
    ScanRepositoryRequestSchema,
)

__all__ = [
    "FileStructureDomainService",
    "FileStructureService",
    "KnowledgeGraphDomainService",
    "FileStructureScaffolderService",
    "FileStructureGraphSyncService",
    "FileStructureImpactAnalyzerService",
    "FileStructureMapResolverService",
    "ImpactAnalysisReportModel",
    "ImpactedNodeModel",
    "FileStructureEntitySchema",
    "KnowledgeGraphEntitySchema",
    "ScaffoldFeatureRequestSchema",
    "ScaffoldPackageRequestSchema",
    "AnalyzeImpactRequestSchema",
    "ScanRepositoryRequestSchema",
]
