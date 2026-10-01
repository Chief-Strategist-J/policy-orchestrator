"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KNOWLEDGE GRAPH SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module builds and maintains the Semantic Policy & Architecture Knowledge
   Graph. It extracts entities (Rules, Categories, Failure Modes, Architecture
   Patterns) from markdown contracts and links them via directed relationships.
   It enables impact analysis, path queries, and graph-guided agent reasoning.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Entity extraction heuristics, graph modeling
     taxonomies, and Cypher query templates are captured in this top blueprint.
     Class methods and functions are 100% comment-free.
   - Graph Schema:
       (:Rule {id, title, file}) ──[:BELONGS_TO]──> (:Category {name})
       (:Rule) ──[:PREVENTS]──> (:FailureMode {type})
       (:Rule) ──[:ENFORCES]──> (:ArchitecturePattern {name})

3. METHOD CONTRACTS:
   - build_graph_from_rules(): Scans markdown knowledge chunks to populate graph.
   - query_graph(): Runs declarative Cypher queries over the knowledge graph.
   - get_category_rules(): Retrieves all rules under a category.
   - get_rule_impact(): Finds all architecture patterns and failure modes tied to a rule.
================================================================================
"""

import re
from typing import List, Dict, Any, Optional

from src.domain.ports.graph_port import (
    GraphStorePort,
    GraphNode,
    GraphRelationship,
    GraphQueryResult,
)
from src.domain.ports.knowledge_port import KnowledgeSourcePort, KnowledgeChunk

class KnowledgeGraphService:
    def __init__(
        self,
        graph_store: GraphStorePort,
        knowledge_source: KnowledgeSourcePort,
    ) -> None:
        self.graph_store = graph_store
        self.knowledge_source = knowledge_source

    def build_graph_from_rules(self) -> Dict[str, int]:
        chunks = self.knowledge_source.load_all_chunks()
        self.graph_store.clear()

        categories_seen = set()
        for chunk in chunks:
            cat_id = f"cat_{chunk.category}"
            if cat_id not in categories_seen:
                self.graph_store.upsert_node(
                    GraphNode(id=cat_id, label="Category", properties={"name": chunk.category})
                )
                categories_seen.add(cat_id)

            rule_node = GraphNode(
                id=chunk.id,
                label="Rule",
                properties={
                    "title": chunk.section_title,
                    "source_file": chunk.source_path,
                    "category": chunk.category,
                },
            )
            self.graph_store.upsert_node(rule_node)

            self.graph_store.upsert_relationship(
                GraphRelationship(
                    source_id=chunk.id,
                    target_id=cat_id,
                    rel_type="BELONGS_TO",
                )
            )

            lower_content = chunk.content.lower()
            if "outbox" in lower_content or "dual write" in lower_content or "concurrency" in lower_content:
                pattern_id = "pat_transactional_outbox"
                self.graph_store.upsert_node(
                    GraphNode(id=pattern_id, label="ArchitecturePattern", properties={"name": "Transactional Outbox"})
                )
                self.graph_store.upsert_relationship(
                    GraphRelationship(source_id=chunk.id, target_id=pattern_id, rel_type="ENFORCES")
                )

            if "comment" in lower_content or "doctrine" in lower_content:
                pattern_id = "pat_zero_inline_comments"
                self.graph_store.upsert_node(
                    GraphNode(id=pattern_id, label="ArchitecturePattern", properties={"name": "Zero Inline Comments Doctrine"})
                )
                self.graph_store.upsert_relationship(
                    GraphRelationship(source_id=chunk.id, target_id=pattern_id, rel_type="ENFORCES")
                )

            if "traceparent" in lower_content or "opentelemetry" in lower_content or "cloudevents" in lower_content:
                pattern_id = "pat_open_standards"
                self.graph_store.upsert_node(
                    GraphNode(id=pattern_id, label="ArchitecturePattern", properties={"name": "Open Standards & W3C Tracing"})
                )
                self.graph_store.upsert_relationship(
                    GraphRelationship(source_id=chunk.id, target_id=pattern_id, rel_type="ENFORCES")
                )

        return {
            "total_nodes": self.graph_store.count_nodes(),
            "total_relationships": self.graph_store.count_relationships(),
        }

    def query_graph(self, query: str, params: Optional[Dict[str, Any]] = None) -> GraphQueryResult:
        return self.graph_store.query_cypher(query, params)

    def get_rule_impact(self, rule_id: str) -> List[Dict[str, Any]]:
        neighbors = self.graph_store.find_neighbors(rule_id, direction="OUTGOING")
        return [{"id": n.id, "label": n.label, "properties": n.properties} for n in neighbors]
