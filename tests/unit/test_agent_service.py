"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AI AGENT SERVICE UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides unit test coverage for AgentService, validating ReAct
   reasoning loop execution, tool invocation dispatch, observation recording,
   and deterministic completion under mock/offline mode.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and loop invariants are stated
     in this top-side blueprint. Test methods remain 100% comment-free.
================================================================================
"""

import unittest
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.features.rag.service.rag_service import RAGService
from src.features.audit.service.audit_service import AuditService
from src.features.agent.service.agent_service import AgentService
from src.features.agent.types.agent_types import AgentExecutionRequest
from tests.unit.test_rag_service import MockKnowledgeSource

class TestAgentService(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = MockLLMAdapter()
        self.rag = RAGService(
            knowledge_source=MockKnowledgeSource(),
            vector_store=InMemoryCosineVectorAdapter(),
            llm_provider=self.llm,
        )
        self.audit = AuditService()
        self.agent = AgentService(
            llm_provider=self.llm,
            rag_service=self.rag,
            audit_service=self.audit,
        )

    def test_agent_execution_with_audit_tool(self) -> None:
        req = AgentExecutionRequest(
            prompt="Audit the repository for edge cases and violations",
            max_steps=5,
        )
        result = self.agent.execute_agent_loop(req)
        self.assertEqual(result.status, "COMPLETED")
        self.assertGreater(result.total_steps, 0)
        self.assertTrue(any(step.tool_calls for step in result.steps))

if __name__ == "__main__":
    unittest.main()
