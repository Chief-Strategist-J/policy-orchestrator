"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RAG SERVICE HYBRID RETRIEVAL UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides unit test coverage for RAGService, verifying markdown
   loading, BM25 sparse index calculation, dense vector scoring, and Reciprocal
   Rank Fusion (RRF) deduplication and ranking.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All testing protocols are in this header.
     Test cases remain 100% comment-free.
================================================================================
"""

import unittest
from typing import List
from src.domain.ports.knowledge_port import KnowledgeSourcePort, KnowledgeChunk
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.features.rag.service.rag_service import RAGService
from src.features.rag.types.rag_types import RAGQueryRequest

class MockKnowledgeSource(KnowledgeSourcePort):
    def load_all_chunks(self) -> List[KnowledgeChunk]:
        return [
            KnowledgeChunk(
                id="c1",
                source_path="openStandards-scalling/open.standard.md",
                section_title="Open Standards and Observability",
                content="# Open Standards\nAll APIs must implement W3C Trace Context, traceparent header, and CloudEvents 1.0.",
                category="openStandards-scalling",
            ),
            KnowledgeChunk(
                id="c2",
                source_path="folderStructure/api-structure.md",
                section_title="Zero Inline Comments Doctrine",
                content="# API Structure\nZero inline comments permitted inside function bodies or loops.",
                category="folderStructure",
            ),
            KnowledgeChunk(
                id="c3",
                source_path="edgeCases/concurrency.md",
                section_title="Distributed Locking and Dual Writes",
                content="# Concurrency\nOutbox pattern must be used to prevent dual-write anomalies.",
                category="edgeCases",
            ),
        ]

    def load_by_pattern(self, pattern: str) -> List[KnowledgeChunk]:
        return self.load_all_chunks()

class TestRAGService(unittest.TestCase):
    def setUp(self) -> None:
        self.knowledge = MockKnowledgeSource()
        self.vector_store = InMemoryCosineVectorAdapter()
        self.llm = MockLLMAdapter()
        self.rag = RAGService(
            knowledge_source=self.knowledge,
            vector_store=self.vector_store,
            llm_provider=self.llm,
        )

    def test_indexing_and_hybrid_retrieval(self) -> None:
        indexed_count = self.rag.index_all_rules()
        self.assertEqual(indexed_count, 3)

        res = self.rag.retrieve_context(
            RAGQueryRequest(query="W3C traceparent cloud events", top_k=1)
        )
        self.assertEqual(res.total_found, 1)
        self.assertEqual(res.documents[0].id, "c1")
        self.assertIn("traceparent", res.formatted_context_block.lower())

    def test_category_filtering(self) -> None:
        self.rag.index_all_rules()
        res = self.rag.retrieve_context(
            RAGQueryRequest(query="inline comments", category_filter="folderStructure", top_k=2)
        )
        self.assertEqual(res.total_found, 1)
        self.assertEqual(res.documents[0].category, "folderStructure")

if __name__ == "__main__":
    unittest.main()
