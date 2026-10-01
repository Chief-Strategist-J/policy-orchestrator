"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RAG DOMAIN TYPES
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines immutable domain dataclasses for the Retrieval-Augmented
   Generation (RAG) subsystem, including queries, retrieval scores, fusion rank
   results, and grounded context packages.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All field specifications and invariant
     constraints are documented in this top-side header.
   - Immutable Frozen Dataclasses: Prevents state mutation across search pipelines.
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class RAGQueryRequest:
    query: str
    top_k: int = 5
    category_filter: Optional[str] = None
    min_relevance_score: float = 0.1
    include_raw_content: bool = True

@dataclass(frozen=True)
class GroundedDocument:
    id: str
    source_file: str
    section_title: str
    content: str
    category: str
    dense_score: float
    sparse_score: float
    rrf_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class RAGContextResponse:
    query: str
    total_found: int
    documents: List[GroundedDocument]
    formatted_context_block: str
    latency_ms: float
