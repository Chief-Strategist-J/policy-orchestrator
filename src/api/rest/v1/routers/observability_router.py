"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 OBSERVABILITY ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the 6 Layer 1 Observability Algorithms
   (ALGO-OBS-16 through ALGO-OBS-21):
   - Fast line-column span tracking (ALGO-OBS-16)
   - Language-agnostic AST extraction (ALGO-OBS-17)
   - Lexical & global symbol resolution (ALGO-OBS-18)
   - Zero-Inline-Comment doctrine linting (ALGO-OBS-19)
   - Module import dependency graphing & cycle detection (ALGO-OBS-20)
   - Hierarchical code outline generation (ALGO-OBS-21)

2. ZERO-INLINE-COMMENT DOCTRINE:
   No inline comments inside functions; all contracts and schemas documented in docblock.
================================================================================
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.api.rest.v1.dependencies import get_code_engine_service
from src.api.rest.v1.routers.search_router import FilePathDTO, DirectoryPathDTO

router = APIRouter()

class ObsSpanTrackDTO(BaseModel):
    content: str = Field(..., description="Source code content")
    offset: int = Field(default=0, description="Byte or character offset")


class ObsAstDTO(BaseModel):
    code: str = Field(..., description="Source code")
    language: str = Field(default="python", description="Programming language")


class ObsSymbolsDTO(BaseModel):
    code: str = Field(..., description="Source code")

@router.post("/algos/observability/span-track")
def obs_span_track(payload: ObsSpanTrackDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-OBS-16", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/observability/ast")
def obs_ast_extract(payload: ObsAstDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-OBS-17", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/observability/symbols")
def obs_symbols_resolve(payload: ObsSymbolsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-OBS-18", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/observability/lint-comments")
@router.post("/algos/lint-comments")
def lint_comments(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    if not os.path.isfile(payload.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.file_path}")
    report = svc.lint_zero_inline_comments(payload.file_path)
    return build_success_envelope(data=report, trace_id=trace_id)


@router.post("/algos/observability/dependencies")
@router.post("/algos/dependencies")
def analyze_dependencies(payload: DirectoryPathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    report = svc.analyze_module_dependencies(payload.directory)
    return build_success_envelope(data=report, trace_id=trace_id)


@router.post("/algos/observability/outline")
@router.post("/algos/outline")
def generate_file_outline(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    if not os.path.isfile(payload.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.file_path}")
    outline = svc.inspect_file_outline(payload.file_path)
    return build_success_envelope(data=outline, trace_id=trace_id)
