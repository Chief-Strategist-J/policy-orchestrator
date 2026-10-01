"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RAG API & DTO SCHEMAS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines Pydantic DTO models for incoming RAG search requests,
   context retrievals, and indexing requests.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Schema constraints, defaults, and serialization
     configurations are declared in this blueprint.
   - Strict Field Validation: Ensures robust type checking and input sanitization.
================================================================================
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RAGSearchRequestDTO(BaseModel):
    query: str = Field(..., description="Natural language search or policy question")
    top_k: int = Field(5, ge=1, le=50, description="Max grounded chunks to retrieve")
    category_filter: Optional[str] = Field(None, description="Optional category filter")
    min_score: float = Field(0.05, ge=0.0, le=1.0, description="Minimum relevance threshold")

class GroundedDocumentDTO(BaseModel):
    id: str
    source_file: str
    section_title: str
    content: str
    category: str
    rrf_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RAGSearchResponseDTO(BaseModel):
    query: str
    total_found: int
    documents: List[GroundedDocumentDTO]
    formatted_context_block: str
    latency_ms: float

class IndexingStatusDTO(BaseModel):
    indexed_documents: int
    categories: List[str]
    status: str
