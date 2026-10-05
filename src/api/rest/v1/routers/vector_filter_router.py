"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 VECTOR FILTER ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the 5 Vector Filter Algorithms
   (ALGO-VEC-FLTR-80 through ALGO-VEC-FLTR-84):
   - Metadata Pre-Filtering (ALGO-VEC-FLTR-80)
   - Oversampled Post-Filtering (ALGO-VEC-FLTR-81)
   - ACORN-Style In-Graph Filtering (ALGO-VEC-FLTR-82)
   - Cost-Based Selectivity Query Planner (ALGO-VEC-FLTR-83)
   - Partitioned Multi-Tenant Index Search (ALGO-VEC-FLTR-84)

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

class VecFilterPreFilterDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    metadata: List[Dict[str, Any]] = Field(..., description="Metadata dictionaries per vector")
    query: List[float] = Field(..., description="Query vector")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    k: int = Field(default=5, description="Top-k matching candidates")


class VecFilterPostFilterDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    metadata: List[Dict[str, Any]] = Field(..., description="Metadata dictionaries per vector")
    query: List[float] = Field(..., description="Query vector")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    k: int = Field(default=5, description="Top-k matching candidates")
    oversample_factor: float = Field(default=4.0, description="Oversampling multiplier")


class VecFilterInGraphDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    metadata: List[Dict[str, Any]] = Field(..., description="Metadata dictionaries per vector")
    adjacency: Dict[str, List[int]] = Field(..., description="Graph adjacency structure")
    entry_point: int = Field(default=0, description="Start traversal entry point node ID")
    query: List[float] = Field(..., description="Query vector")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    k: int = Field(default=5, description="Top-k matching candidates")
    ef_search: int = Field(default=16, description="Beam search width")


class VecFilterSelectivityPlanDTO(BaseModel):
    total_vectors: int = Field(..., description="Total size of vector dataset")
    metadata_sample: List[Dict[str, Any]] = Field(default_factory=list, description="Sample of metadata records")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    is_security_filter: bool = Field(default=False, description="Whether filter enforces strict security/tenant boundary")


class VecFilterPartitionedDTO(BaseModel):
    partitions: Dict[str, List[Dict[str, Any]]] = Field(..., description="Partition map keyed by tenant/collection")
    target_partition: str = Field(..., description="Partition key to query")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matching candidates")

@router.post("/algos/vector-filter/pre-filter")
def vector_filter_pre_filter_endpoint(payload: VecFilterPreFilterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-80", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/post-filter")
def vector_filter_post_filter_endpoint(payload: VecFilterPostFilterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-81", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/in-graph")
def vector_filter_in_graph_endpoint(payload: VecFilterInGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-82", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/selectivity-plan")
def vector_filter_selectivity_plan_endpoint(payload: VecFilterSelectivityPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-83", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/partitioned")
def vector_filter_partitioned_endpoint(payload: VecFilterPartitionedDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-84", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)
