"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 BASE VECTOR ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the 9 Base Vector Algorithms
   (ALGO-VEC-01 through ALGO-VEC-09):
   - L2 vector normalization (ALGO-VEC-01)
   - Corpus mean centering & anisotropy removal (ALGO-VEC-02)
   - Layer normalization & standardization (ALGO-VEC-03)
   - Min-Max & Z-Score vector scaling (ALGO-VEC-04)
   - Matryoshka Representation Learning slicing (ALGO-VEC-05)
   - Uniform scalar quantization SQ8/SQ4 (ALGO-VEC-06)
   - 1-Bit binary quantization (ALGO-VEC-07)
   - Token pooling (Mean/CLS/Last-Token) (ALGO-VEC-08)
   - Text chunking & semantic breakpoint detection (ALGO-VEC-09)

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

class VectorNormalizeDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense float vector to normalize")
    eps: float = Field(default=1e-12, description="Zero-division guard epsilon")


class VectorCenterDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Batch of vectors for corpus mean centering")


class VectorLayerNormDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense input vector")
    gamma: Optional[List[float]] = Field(default=None, description="Learned scale parameter")
    beta: Optional[List[float]] = Field(default=None, description="Learned shift parameter")
    eps: float = Field(default=1e-5, description="Epsilon stability factor")


class VectorScaleDTO(BaseModel):
    vector: List[float] = Field(..., description="Input feature vector")
    min_val: float = Field(default=0.0, description="Target minimum range")
    max_val: float = Field(default=1.0, description="Target maximum range")
    method: str = Field(default="minmax", description="Scaling method ('minmax' or 'zscore')")


class VectorSliceDTO(BaseModel):
    vector: List[float] = Field(..., description="High-dimensional embedding vector")
    target_dim: int = Field(default=64, description="Target lower dimension prefix")
    renormalize: bool = Field(default=True, description="Apply L2 normalization after slicing")


class VectorScalarQuantizeDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense float vector")
    bits: int = Field(default=8, description="Quantization bit depth (8 or 4)")


class VectorBinaryQuantizeDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense float vector")


class VectorPoolDTO(BaseModel):
    token_embeddings: List[List[float]] = Field(..., description="Sequence token embeddings (seq_len x dim)")
    attention_mask: Optional[List[int]] = Field(default=None, description="Attention mask (1 for token, 0 for pad)")
    pooling_strategy: str = Field(default="mean", description="Pooling method ('mean', 'cls', 'last')")


class VectorChunkDTO(BaseModel):
    text: str = Field(..., description="Document text to chunk")
    max_chunk_size: int = Field(default=200, description="Maximum characters/tokens per chunk")
    overlap: int = Field(default=40, description="Overlap between consecutive chunks")

@router.post("/algos/vector/normalize")
def normalize_vector_endpoint(payload: VectorNormalizeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    normalized = svc.normalize_vector(payload.vector, eps=payload.eps)
    return build_success_envelope(
        data={"original_dimension": len(payload.vector), "normalized_vector": normalized},
        trace_id=trace_id,
    )


@router.post("/algos/vector/center")
def center_vectors_endpoint(payload: VectorCenterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    centered = svc.center_vectors(payload.vectors)
    return build_success_envelope(
        data={"total_vectors": len(payload.vectors), "centered_vectors": centered},
        trace_id=trace_id,
    )


@router.post("/algos/vector/layer-norm")
def layer_norm_endpoint(payload: VectorLayerNormDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    norm = svc.layer_norm_vector(payload.vector, gamma=payload.gamma, beta=payload.beta, eps=payload.eps)
    return build_success_envelope(
        data={"dimension": len(payload.vector), "normalized_vector": norm},
        trace_id=trace_id,
    )


@router.post("/algos/vector/scale")
def scale_vector_endpoint(payload: VectorScaleDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    scaled = svc.scale_vector(payload.vector, min_val=payload.min_val, max_val=payload.max_val, method=payload.method)
    return build_success_envelope(
        data={"scaled_vector": scaled, "method": payload.method},
        trace_id=trace_id,
    )


@router.post("/algos/vector/slice")
def slice_vector_endpoint(payload: VectorSliceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    sliced = svc.slice_vector(payload.vector, target_dim=payload.target_dim, renormalize=payload.renormalize)
    return build_success_envelope(
        data={"original_dimension": len(payload.vector), "target_dimension": payload.target_dim, "sliced_vector": sliced},
        trace_id=trace_id,
    )


@router.post("/algos/vector/quantize/scalar")
def quantize_scalar_endpoint(payload: VectorScalarQuantizeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.quantize_scalar(payload.vector, bits=payload.bits)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector/quantize/binary")
def quantize_binary_endpoint(payload: VectorBinaryQuantizeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.quantize_binary(payload.vector)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector/pool")
def pool_tokens_endpoint(payload: VectorPoolDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.pool_tokens(payload.token_embeddings, attention_mask=payload.attention_mask, pooling_strategy=payload.pooling_strategy)
    return build_success_envelope(
        data={"pooling_strategy": payload.pooling_strategy, "pooled_vector": res},
        trace_id=trace_id,
    )


@router.post("/algos/vector/chunk")
def chunk_text_endpoint(payload: VectorChunkDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    chunks = svc.chunk_text(
        text=payload.text,
        max_chunk_size=payload.max_chunk_size,
        overlap=payload.overlap,
    )
    return build_success_envelope(
        data={"total_chunks": len(chunks), "chunks": chunks},
        trace_id=trace_id,
    )
