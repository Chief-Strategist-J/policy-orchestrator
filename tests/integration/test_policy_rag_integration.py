"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REAL POLICY RULES RAG INTEGRATION TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module tests end-to-end knowledge loading, indexing, and hybrid retrieval
   against the real `policies/rules` markdown catalog. It verifies that rule
   contracts are correctly parsed into sections, indexed, and retrieved.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and invariant checks are
     declared in this header. Test methods are 100% comment-free.
================================================================================
"""

import os
import unittest
from src.infra.adapters.knowledge.policy_rules_loader import PolicyRulesMarkdownLoader
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.features.rag.service.rag_service import RAGService
from src.features.rag.types.rag_types import RAGQueryRequest

class TestPolicyRAGIntegration(unittest.TestCase):
    def setUp(self) -> None:
        rules_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../rules"))
        self.loader = PolicyRulesMarkdownLoader(base_rules_dir=rules_dir)
        self.vector_store = InMemoryCosineVectorAdapter()
        self.llm = MockLLMAdapter(dimension=64)
        self.rag = RAGService(
            knowledge_source=self.loader,
            vector_store=self.vector_store,
            llm_provider=self.llm,
        )

    def test_live_rules_indexing_and_search(self) -> None:
        count = self.rag.index_all_rules()
        self.assertGreater(count, 10)

        res = self.rag.retrieve_context(
            RAGQueryRequest(query="open standards traceparent cloudevents", top_k=3)
        )
        self.assertGreater(res.total_found, 0)
        self.assertTrue(len(res.formatted_context_block) > 50)

if __name__ == "__main__":
    unittest.main()
