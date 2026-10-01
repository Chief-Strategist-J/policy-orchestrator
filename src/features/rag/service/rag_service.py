"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HYBRID RAG SERVICE & RRF RANKING
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements high-precision, grounded Retrieval-Augmented Generation
   over markdown policy rules (`policies/rules/`). It combines Dense Semantic
   Retrieval (via VectorStorePort and LLMProviderPort embeddings) and Sparse
   Lexical Retrieval (BM25 term-frequency scoring) unified via Reciprocal Rank
   Fusion (RRF).

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All mathematical formulas, tokenization rules,
     inverted indexing routines, and ranking algorithms are articulated in this
     top-side blueprint. Function and loop bodies are strictly comment-free.
   - Reciprocal Rank Fusion (RRF):
       Score(doc) = Σ (1 / (K_RRF + Rank_i(doc)))
       where K_RRF = 60 (standard constant).
   - Inverted Index Tokenizer: Lowercase alphanumeric token extraction with stopword
     suppression for fast in-memory BM25-style lexical scoring.
   - Grounded Context Assembly: Produces markdown context blocks referencing source
     files and section titles for verifiable agent reasoning.

3. METHOD CONTRACTS:
   - index_all_rules(): Parses knowledge source, computes embeddings in batches,
     builds inverted index, and populates the vector store.
   - retrieve_context(): Executes hybrid search, computes RRF scores, and formats
     grounded prompt context.
================================================================================
"""

import re
import time
import math
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from src.domain.ports.llm_port import LLMProviderPort
from src.domain.ports.vector_port import VectorStorePort, VectorDocument
from src.domain.ports.knowledge_port import KnowledgeSourcePort, KnowledgeChunk
from src.features.rag.types.rag_types import (
    RAGQueryRequest,
    GroundedDocument,
    RAGContextResponse,
)

class RAGService:
    def __init__(
        self,
        knowledge_source: KnowledgeSourcePort,
        vector_store: VectorStorePort,
        llm_provider: LLMProviderPort,
        rrf_k: int = 60,
    ) -> None:
        self.knowledge_source = knowledge_source
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.rrf_k = rrf_k
        self._chunks_map: Dict[str, KnowledgeChunk] = {}
        self._inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self._doc_lengths: Dict[str, int] = {}
        self._avg_doc_length: float = 1.0

    def _tokenize(self, text: str) -> List[str]:
        return [t for t in re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())]

    def index_all_rules(self, batch_size: int = 32) -> int:
        chunks = self.knowledge_source.load_all_chunks()
        if not chunks:
            return 0

        self._chunks_map.clear()
        self._inverted_index.clear()
        self._doc_lengths.clear()
        self.vector_store.clear()

        total_length = 0
        for chunk in chunks:
            self._chunks_map[chunk.id] = chunk
            tokens = self._tokenize(chunk.content)
            self._doc_lengths[chunk.id] = len(tokens)
            total_length += len(tokens)
            for token in set(tokens):
                self._inverted_index[token].add(chunk.id)

        self._avg_doc_length = max(1.0, total_length / max(1, len(chunks)))

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.content for c in batch]
            embeddings = self.llm_provider.get_embeddings(texts)
            vector_docs = [
                VectorDocument(
                    id=chunk.id,
                    content=chunk.content,
                    embedding=embeddings[idx],
                    metadata={
                        "source_file": chunk.source_path,
                        "section_title": chunk.section_title,
                        "category": chunk.category,
                    },
                )
                for idx, chunk in enumerate(batch)
            ]
            self.vector_store.upsert(vector_docs)

        return len(chunks)

    def _score_bm25(self, query_tokens: List[str], doc_id: str) -> float:
        chunk = self._chunks_map.get(doc_id)
        if not chunk:
            return 0.0

        doc_tokens = self._tokenize(chunk.content)
        doc_len = self._doc_lengths.get(doc_id, 1)
        k1 = 1.5
        b = 0.75
        score = 0.0

        for token in query_tokens:
            doc_freq = len(self._inverted_index.get(token, set()))
            if doc_freq == 0:
                continue
            idf = math.log(1.0 + (len(self._chunks_map) - doc_freq + 0.5) / (doc_freq + 0.5))
            tf = doc_tokens.count(token)
            denom = tf + k1 * (1.0 - b + b * (doc_len / self._avg_doc_length))
            score += idf * ((tf * (k1 + 1.0)) / max(0.0001, denom))

        return score

    def retrieve_context(self, request: RAGQueryRequest) -> RAGContextResponse:
        start_time = time.perf_counter()
        
        if not self._chunks_map:
            self.index_all_rules()

        query_tokens = self._tokenize(request.query)
        sparse_scores: Dict[str, float] = {}
        for doc_id in self._chunks_map:
            s = self._score_bm25(query_tokens, doc_id)
            if s > 0.0:
                sparse_scores[doc_id] = s

        sorted_sparse = sorted(sparse_scores.items(), key=lambda x: x[1], reverse=True)
        sparse_rank_map = {doc_id: rank + 1 for rank, (doc_id, _) in enumerate(sorted_sparse)}

        query_embedding = self.llm_provider.get_embeddings([request.query])[0]
        filter_meta = {"category": request.category_filter} if request.category_filter else None
        dense_results = self.vector_store.query_by_vector(
            vector=query_embedding,
            top_k=request.top_k * 3,
            filter_metadata=filter_meta,
        )

        dense_rank_map = {res.document.id: rank + 1 for rank, res in enumerate(dense_results) if res.score > 0.05}
        dense_score_map = {res.document.id: res.score for res in dense_results if res.score > 0.05}

        all_candidate_ids = set(sparse_rank_map.keys()) | set(dense_rank_map.keys())
        grounded_docs: List[GroundedDocument] = []

        for doc_id in all_candidate_ids:
            chunk = self._chunks_map.get(doc_id)
            if not chunk:
                continue
            if request.category_filter and chunk.category != request.category_filter:
                continue

            dense_rank = dense_rank_map.get(doc_id, 9999)
            sparse_rank = sparse_rank_map.get(doc_id, 9999)
            rrf_score = (1.0 / (self.rrf_k + dense_rank)) + (1.0 / (self.rrf_k + sparse_rank))

            if rrf_score < request.min_relevance_score and len(grounded_docs) >= request.top_k:
                continue

            grounded_docs.append(
                GroundedDocument(
                    id=doc_id,
                    source_file=chunk.source_path,
                    section_title=chunk.section_title,
                    content=chunk.content,
                    category=chunk.category,
                    dense_score=dense_score_map.get(doc_id, 0.0),
                    sparse_score=sparse_scores.get(doc_id, 0.0),
                    rrf_score=rrf_score,
                    metadata=chunk.metadata,
                )
            )

        grounded_docs.sort(key=lambda d: d.rrf_score, reverse=True)
        selected_docs = grounded_docs[: request.top_k]

        context_lines = []
        for doc in selected_docs:
            context_lines.append(
                f"### [Policy Document: {doc.source_file}] {doc.section_title}\n"
                f"**Category**: `{doc.category}` | **Relevance Score**: `{doc.rrf_score:.4f}`\n\n"
                f"{doc.content}\n"
                f"---\n"
            )

        formatted_context = "\n".join(context_lines)
        latency = (time.perf_counter() - start_time) * 1000.0

        return RAGContextResponse(
            query=request.query,
            total_found=len(selected_docs),
            documents=selected_docs,
            formatted_context_block=formatted_context,
            latency_ms=round(latency, 2),
        )
