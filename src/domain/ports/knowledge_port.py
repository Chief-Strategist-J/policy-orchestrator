"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KNOWLEDGE SOURCE PORT (HEXAGONAL ARCHITECTURE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port for Knowledge Ingestion
   and Policy Rule Parsing. It guarantees 100% decoupling from specific file
   formats, remote CMS, or Git repositories, serving markdown policy rules as
   structured domain chunks for RAG indexing.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All loading specifications, document chunk
     models, and taxonomy classifications are documented in this top-side header.
     Interface declarations remain 100% comment-free and pure.
   - Grounding Integrity: Provides deterministic chunking with section headings,
     file provenance, line references, and metadata taxonomy.

3. METHOD CONTRACTS:
   - load_all_chunks(): Recursively parses knowledge files into structured chunks.
   - load_by_pattern(): Filters source loading using standard glob patterns.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    source_path: str
    section_title: str
    content: str
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class KnowledgeSourcePort(ABC):
    @abstractmethod
    def load_all_chunks(self) -> List[KnowledgeChunk]:
        pass

    @abstractmethod
    def load_by_pattern(self, pattern: str) -> List[KnowledgeChunk]:
        pass
