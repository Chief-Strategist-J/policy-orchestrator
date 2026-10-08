"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE REST ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dedicated FastAPI router mounting File Structure scaffolding, validation,
   and Knowledge Graph impact analysis endpoints.
   Adheres strictly to RFC standards with zero inline comments in endpoints.
================================================================================
"""

from fastapi import APIRouter, Request, Depends, status
from src.api.rest.v1.handlers.file_structure_handler import FileStructureRestHandler
from src.features.file_structure.service.file_structure_service import FileStructureDomainService
from src.features.file_structure.schema.file_structure_schema import (
    AnalyzeImpactRequestSchema,
    ScanRepositoryRequestSchema,
    ScaffoldFeatureRequestSchema,
    ScaffoldPackageRequestSchema,
    LinkFilesRequestSchema,
    CreateFileRequestSchema,
)
from src.api.rest.envelope import APIResponseEnvelope
from src.api.rest.v1.dependencies import get_graph_store

router = APIRouter(prefix="/file-structure", tags=["File Structure & Knowledge Graph"])

def get_file_structure_handler(graph_store=Depends(get_graph_store)) -> FileStructureRestHandler:
    service = FileStructureDomainService(graph_store=graph_store)
    return FileStructureRestHandler(service=service)

@router.post("/scaffold/feature", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
def scaffold_feature_structure(
    payload: ScaffoldFeatureRequestSchema,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_scaffold_feature(req=req, payload=payload)

@router.post("/scaffold/package", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
def scaffold_package_structure(
    payload: ScaffoldPackageRequestSchema,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_scaffold_package(req=req, payload=payload)

@router.post("/impact-analysis", response_model=APIResponseEnvelope)
def analyze_architectural_impact(
    payload: AnalyzeImpactRequestSchema,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_analyze_impact(req=req, payload=payload)

@router.post("/scan-repository", response_model=APIResponseEnvelope)
def scan_repository_workspace(
    payload: ScanRepositoryRequestSchema,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_scan_repository(req=req, payload=payload)

@router.post("/link-files", response_model=APIResponseEnvelope)
def link_architectural_files(
    payload: LinkFilesRequestSchema,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_link_files(req=req, payload=payload)

@router.post("/create-file", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
def create_architectural_file(
    payload: CreateFileRequestSchema,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_create_file(req=req, payload=payload)

@router.get("/feature/{feature_name}", response_model=APIResponseEnvelope)
def get_feature_architecture_map(
    feature_name: str,
    req: Request,
    handler: FileStructureRestHandler = Depends(get_file_structure_handler),
):
    return handler.handle_get_feature_map(req=req, feature_name=feature_name)

