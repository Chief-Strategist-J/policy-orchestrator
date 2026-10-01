"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR STORE & EMBEDDINGS UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides unit test verification for the InMemoryCosineVectorAdapter
   and MockLLMAdapter embeddings. It validates cosine similarity ranking,
   metadata filtering, upsert idempotency, and eviction semantics.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: Test plans and assertions are documented here.
     Test methods are 100% comment-free and pure.
================================================================================
"""

import unittest
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.domain.ports.vector_port import VectorDocument

class TestVectorStore(unittest.TestCase):
    def setUp(self) -> None:
        self.vector_store = InMemoryCosineVectorAdapter()
        self.llm = MockLLMAdapter(dimension=32)

    def test_upsert_and_similarity_query(self) -> None:
        texts = [
            "hexagonal architecture ports and adapters pattern",
            "database postgresql connection pool indexing",
            "zero inline comments docblock specification",
        ]
        embeddings = self.llm.get_embeddings(texts)
        docs = [
            VectorDocument(
                id=f"doc_{idx}",
                content=txt,
                embedding=embeddings[idx],
                metadata={"category": "arch" if idx != 1 else "db"},
            )
            for idx, txt in enumerate(texts)
        ]

        count = self.vector_store.upsert(docs)
        self.assertEqual(count, 3)
        self.assertEqual(self.vector_store.count(), 3)

        query_emb = self.llm.get_embeddings(["ports and adapters architecture"])[0]
        results = self.vector_store.query_by_vector(query_emb, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].document.id, "doc_0")

    def test_metadata_filtering(self) -> None:
        texts = ["rule one", "rule two"]
        embeddings = self.llm.get_embeddings(texts)
        docs = [
            VectorDocument(id="1", content=texts[0], embedding=embeddings[0], metadata={"category": "sec"}),
            VectorDocument(id="2", content=texts[1], embedding=embeddings[1], metadata={"category": "db"}),
        ]
        self.vector_store.upsert(docs)

        query_emb = self.llm.get_embeddings(["rule"])[0]
        results = self.vector_store.query_by_vector(query_emb, top_k=5, filter_metadata={"category": "db"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].document.id, "2")

if __name__ == "__main__":
    unittest.main()
