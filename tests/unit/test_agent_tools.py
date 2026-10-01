"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AGENT TOOLS & REGISTRY UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides unit test verification for WebSearchPort and ToolRegistryPort
   adapters, validating search response parsing, dynamic tool registration, and
   agent tool execution.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and testing blueprints are in
     this header. Test methods are 100% comment-free and pure.
================================================================================
"""

import unittest
from src.domain.ports.tool_registry_port import DynamicToolRecord
from src.infra.adapters.search.mock_search_adapter import MockWebSearchAdapter
from src.infra.adapters.tools.in_memory_tool_registry_adapter import InMemoryToolRegistryAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.features.rag.service.rag_service import RAGService
from src.features.audit.service.audit_service import AuditService
from src.features.agent.service.agent_service import AgentService
from src.features.agent.types.agent_types import AgentExecutionRequest
from tests.unit.test_rag_service import MockKnowledgeSource

class TestAgentTools(unittest.TestCase):
    def setUp(self) -> None:
        self.search = MockWebSearchAdapter()
        self.tool_reg = InMemoryToolRegistryAdapter()
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
            search_provider=self.search,
            tool_registry=self.tool_reg,
        )

    def test_search_adapter(self) -> None:
        res = self.search.search("traceparent header")
        self.assertGreater(res.total_results, 0)
        self.assertIn("traceparent", res.results[0].snippet.lower())

    def test_dynamic_tool_registration(self) -> None:
        record = DynamicToolRecord(
            name="custom_ast_searcher",
            description="Custom searcher for AST tokens",
            parameters_schema={"type": "object", "properties": {"token": {"type": "string"}}},
            category="ast_searcher",
            source_code="def run(token): return {'found': True}",
            created_at="1700000000",
        )
        self.tool_reg.register_tool(record)
        self.assertEqual(len(self.tool_reg.list_tools()), 1)
        self.assertEqual(self.tool_reg.get_tool("custom_ast_searcher").name, "custom_ast_searcher")

if __name__ == "__main__":
    unittest.main()
