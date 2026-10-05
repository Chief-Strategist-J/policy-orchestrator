"""
===============================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR STORE PORT (HEXAGONAL ARCHITECTURE)
===============================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port for Vector Storage and
   Similarity Retrieval. It guarantees 100% decoupling from specific vector
   databases (Qdrant, ChromaDB, PGVector, Pinecone, Weaviate, In-Memory Cosine),
   preventing vendor lock-in as required by open.standard.md and api-structure.md.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All protocol specifications, query models,
     quantization options, and distance constraints are documented in this top-side header.
     Interface declarations remain 100% comment-free and pure.
   - Ports & Adapters Isolation: Domain business logic depends solely on this
     abstract contract. Concrete vector engines live strictly in infra adapters.
   - Vector Dimensionality & Metric Neutrality: The port abstracts over cosine,
     dot-product, and Euclidean similarity scoring models.
   - Advanced Quantization & Rescore Support: Native interface contracts for
     Binary Quantization (BQ), Scalar Quantization (SQ/INT8), and oversampled rescoring.

3. METHOD CONTRACTS:
   - upsert(): Ingests or updates a batch of vector documents with metadata.
   - query_by_vector(): Performs nearest-neighbor similarity search with top-k.
   - query_with_quantization(): Performs accelerated quantized search with optional exact rescoring.
   - batch_query(): Performs concurrent multi-vector similarity search.
   - create_collection(): Initializes vector collection space with metric and quantization config.
   - delete(): Evicts documents by unique identifier.
   - count(): Returns total indexed vector documents.
   - clear(): Resets the index space.
===============================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class VectorDocument:
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VectorQueryResult:
    document: VectorDocument
    score: float


@dataclass(frozen=True)
class QuantizationConfig:
    enabled: bool = True
    quantization_type: str = "binary"
    always_ram: bool = True
    rescore: bool = True
    oversampling: float = 2.0


class VectorStorePort(ABC):
    @abstractmethod
    def upsert(self, documents: List[VectorDocument]) -> int:
        pass

    @abstractmethod
    def query_by_vector(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorQueryResult]:
        pass

    @abstractmethod
    def query_with_quantization(
        self,
        vector: List[float],
        top_k: int = 5,
        rescore: bool = True,
        oversampling: float = 2.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorQueryResult]:
        pass

    @abstractmethod
    def batch_query(
        self,
        vectors: List[List[float]],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorQueryResult]]:
        pass

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
        quantization: Optional[QuantizationConfig] = None,
    ) -> bool:
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> int:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
