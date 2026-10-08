"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE REPOSITORY ADAPTER (HEXAGONAL)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Concrete database adapter implementing FileStructureRepositoryPort.
   Binds to GraphStorePort (Neo4j or In-Memory) to persist and query nodes/edges.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Hexagonal Adapter: Implements the interface port strictly.
   - Zero-Inline-Comment Doctrine: Header documents all query contracts.
================================================================================
"""

from typing import List, Dict, Any, Optional
from src.features.file_structure.repository.file_structure_repository_port import FileStructureRepositoryPort
from src.domain.ports.graph_port import GraphStorePort, GraphNode, GraphRelationship

class FileStructureRepositoryAdapter(FileStructureRepositoryPort):
    def __init__(self, graph_store: GraphStorePort) -> None:
        self.graph_store = graph_store

    def save_node(
        self,
        node_id: str,
        label: str,
        file_path: str,
        feature_name: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        props = properties or {}
        props["feature_name"] = feature_name
        props["file_path"] = file_path
        node = GraphNode(id=node_id, label=label, properties=props)
        self.graph_store.upsert_node(node)

    def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        node = self.graph_store.get_node(node_id)
        if not node:
            return None
        return {
            "id": node.id,
            "label": node.label,
            "properties": node.properties,
        }

    def save_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        rel = GraphRelationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=relationship_type,
            properties=properties or {},
        )
        self.graph_store.upsert_relationship(rel)

    def list_upstream_dependencies(self, target_id: str) -> List[Dict[str, Any]]:
        rels = self.graph_store.get_incoming_relationships(target_id)
        return [{"source_id": r.source_id, "relationship": r.rel_type, "properties": r.properties} for r in rels]

    def list_downstream_dependents(self, source_id: str) -> List[Dict[str, Any]]:
        rels = self.graph_store.get_outgoing_relationships(source_id)
        return [{"target_id": r.target_id, "relationship": r.rel_type, "properties": r.properties} for r in rels]

    def clear_all(self) -> None:
        self.graph_store.clear()

KnowledgeGraphRepository = FileStructureRepositoryAdapter
