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
from src.features.file_structure.service.file_structure_service import FileStructureDomainService

class TestFileStructureGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.graph_store = InMemoryGraphAdapter()
        self.service = FileStructureDomainService(
            graph_store=self.graph_store,
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

    def test_feature_scaffolding_and_graph_sync(self) -> None:
        result = self.service.scaffold_feature(feature_name="test_order", base_dir="/tmp/test_src")
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["graph_synced"])

        f_map = self.service.get_feature_map("test_order")
        self.assertEqual(f_map["feature"], "test_order")
        self.assertIn("router", f_map)
        self.assertIn("handler", f_map)
        self.assertIn("service", f_map)

    def test_package_scaffolding_and_graph_sync(self) -> None:
        pkg_result = self.service.scaffold_package(package_name="test_pkg", base_dir="/tmp/test_pkg")
        self.assertEqual(pkg_result["status"], "success")
        self.assertTrue(pkg_result["graph_synced"])

    def test_link_kafka_event_and_dependencies(self) -> None:
        self.service.link_kafka_event(
            feature_name="billing",
            event_name="OrderPlaced",
            topic_name="prod.billing.order.created.v1",
        )
        self.assertIsNotNone(self.graph_store.get_node("producer_billing_orderplaced"))
        self.assertIsNotNone(self.graph_store.get_node("topic_prod_billing_order_created_v1"))

        self.service.link_migration("billing", "database/migrations/0001_create_billing_table.sql")
        self.assertIsNotNone(self.graph_store.get_node("migration_0001_create_billing_table"))

        self.service.link_cross_feature_event(
            publisher_feature="billing",
            consumer_feature="notifications",
            event_name="OrderPlaced",
            topic_name="prod.billing.order.created.v1",
        )
        self.assertIsNotNone(self.graph_store.get_node("consumer_notifications_orderplaced"))

        self.service.link_shared("billing", "src/shared/utils/date_formatter.py")
        self.assertIsNotNone(self.graph_store.get_node("shared_date_formatter"))

if __name__ == "__main__":
    unittest.main()
