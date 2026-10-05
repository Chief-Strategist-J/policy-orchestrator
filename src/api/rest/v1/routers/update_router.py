"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 UPDATE ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the 3 Layer 1 Update Algorithms
   (ALGO-UPD-22 through ALGO-UPD-24):
   - CST pattern matching and syntax replacement (ALGO-UPD-22)
   - Deterministic atomic batch patching (ALGO-UPD-23)
   - Unified GNU/Git context diff generation (ALGO-UPD-24)

2. ZERO-INLINE-COMMENT DOCTRINE:
   No inline comments inside functions; all contracts and schemas documented in docblock.
================================================================================
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from ..dependencies import get_code_engine_service

router = APIRouter()

class PatchOperationDTO(BaseModel):
    file_path: str = Field(..., description="File to patch")
    find_pattern: str = Field(..., description="Target pattern")
    replace_text: str = Field(..., description="Replacement text")
    expected_sha256: Optional[str] = Field(default=None, description="Precondition SHA-256")
    is_regex: bool = Field(default=False, description="Is regex pattern")


class BatchPatchRequestDTO(BaseModel):
    operations: List[PatchOperationDTO] = Field(..., description="List of patch operations")
    dry_run: bool = Field(default=False, description="Simulate patch without disk write")


class DiffRequestDTO(BaseModel):
    original_content: str = Field(..., description="Original text")
    modified_content: str = Field(..., description="Modified text")
    file_path: str = Field(default="file", description="File path identifier")

class UpdateCstMatchDTO(BaseModel):
    code: str = Field(..., description="Source code")
    node_type: str = Field(default="function", description="Target CST node type")

@router.post("/algos/update/cst-match")
def update_cst_match(payload: UpdateCstMatchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-UPD-22", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/update/patch")
def apply_patch(payload: BatchPatchRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    raw_ops = [op.model_dump() for op in payload.operations]
    results = svc.apply_batch_patch(raw_ops, dry_run=payload.dry_run)
    return build_success_envelope(
        data={"total_operations": len(results), "dry_run": payload.dry_run, "results": results},
        trace_id=trace_id,
    )


@router.post("/algos/update/diff")
def generate_diff(payload: DiffRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    diff = svc.generate_diff(
        original_content=payload.original_content,
        modified_content=payload.modified_content,
        file_path=payload.file_path,
    )
    return build_success_envelope(data=diff, trace_id=trace_id)
