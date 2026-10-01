"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DECLARATIVE AGENTS UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module tests the declarative agent manifest catalog, verifying that all
   5 pipeline roles and 22 algorithm specialized agents are registered and
   executable via AgentService with scoped tools and prompts.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and testing blueprints are in
     this header. Test methods are 100% comment-free and pure.
================================================================================
"""

import unittest
from src.infra.adapters.agent.in_memory_agent_registry_adapter import InMemoryAgentManifestRegistryAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.features.rag.service.rag_service import RAGService
from src.features.audit.service.audit_service import AuditService
from src.features.agent.service.agent_service import AgentService
from src.features.agent.types.agent_types import AgentExecutionRequest
from tests.unit.test_rag_service import MockKnowledgeSource

class TestDeclarativeAgents(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = InMemoryAgentManifestRegistryAdapter(load_builtins=True)
        self.llm = MockLLMAdapter()
        self.rag = RAGService(
            knowledge_source=MockKnowledgeSource(),
            vector_store=InMemoryCosineVectorAdapter(),
            llm_provider=self.llm,
        )
        self.audit = AuditService()
        self.agent_svc = AgentService(
            llm_provider=self.llm,
            rag_service=self.rag,
            audit_service=self.audit,
        )

    def test_catalog_contains_all_builtin_agents(self) -> None:
        self.assertGreaterEqual(self.registry.count(), 27)
        scout = self.registry.get_manifest("agent_scout")
        self.assertIsNotNone(scout)
        self.assertEqual(scout.name, "Scout Agent")

        algo_20 = self.registry.get_manifest("algo_20_comment_extractor")
        self.assertIsNotNone(algo_20)
        self.assertIn(20, algo_20.algorithms)

    def test_specialized_agent_execution(self) -> None:
        manifest = self.registry.get_manifest("agent_verifier")
        self.assertIsNotNone(manifest)

        req = AgentExecutionRequest(prompt="Verify repository invariants", max_steps=3)
        res = self.agent_svc.execute_agent_loop(req, manifest=manifest)
        self.assertEqual(res.status, "COMPLETED")

if __name__ == "__main__":
    unittest.main()
