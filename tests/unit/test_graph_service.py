"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KNOWLEDGE GRAPH UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides unit test verification for InMemoryGraphAdapter and
   KnowledgeGraphService, testing node/relationship insertion, BFS shortest path,
   graph construction from knowledge chunks, and impact queries.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and testing blueprints are in
     this header. Test methods are 100% comment-free and pure.
================================================================================
"""

import unittest
from src.domain.ports.graph_port import GraphNode, GraphRelationship
from src.infra.adapters.graph.in_memory_graph_adapter import InMemoryGraphAdapter
from src.features.knowledge_graph.service.knowledge_graph_service import KnowledgeGraphService
from tests.unit.test_rag_service import MockKnowledgeSource

class TestKnowledgeGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.graph_store = InMemoryGraphAdapter()
        self.knowledge = MockKnowledgeSource()
        self.service = KnowledgeGraphService(
            graph_store=self.graph_store,
            knowledge_source=self.knowledge,
        )

    def test_node_edge_and_shortest_path(self) -> None:
        self.graph_store.upsert_node(GraphNode(id="A", label="Rule"))
        self.graph_store.upsert_node(GraphNode(id="B", label="Pattern"))
        self.graph_store.upsert_node(GraphNode(id="C", label="Pattern"))

        self.graph_store.upsert_relationship(GraphRelationship(source_id="A", target_id="B", rel_type="LEADS_TO"))
        self.graph_store.upsert_relationship(GraphRelationship(source_id="B", target_id="C", rel_type="LEADS_TO"))

        path = self.graph_store.find_shortest_path("A", "C")
        self.assertEqual(len(path), 3)
        self.assertEqual([n.id for n in path], ["A", "B", "C"])

    def test_build_graph_from_rules(self) -> None:
        summary = self.service.build_graph_from_rules()
        self.assertGreater(summary["total_nodes"], 3)
        self.assertGreater(summary["total_relationships"], 0)

        impact = self.service.get_rule_impact("c3")
        self.assertGreater(len(impact), 0)

if __name__ == "__main__":
    unittest.main()
