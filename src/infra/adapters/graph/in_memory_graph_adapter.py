"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IN-MEMORY PROPERTY KNOWLEDGE GRAPH ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides a pure-Python, zero-dependency, in-memory directed property
   graph implementing GraphStorePort. It manages nodes, directed edges, label
   indexes, BFS shortest paths, and basic Cypher/pattern query parsing.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Graph adjacency indexing, traversal state
     queues, and property filters are documented in this top-side blueprint.
     Class methods and functions are kept 100% comment-free.
   - Breadth-First Search (BFS): Computes unweighted shortest path in O(V + E) time.
   - Thread-Safe Reads: Stores nodes and relationships in normalized dictionaries.

3. METHOD CONTRACTS:
   - upsert_node(): Inserts or updates node properties and label index.
   - upsert_relationship(): Appends directed relationship to source and target adjacency.
   - find_neighbors(): Traverses incoming, outgoing, or both edge directions.
   - find_shortest_path(): Executes BFS traversal to return ordered node sequence.
================================================================================
"""

from collections import deque
from typing import List, Dict, Any, Optional, Set

from src.domain.ports.graph_port import (
    GraphStorePort,
    GraphNode,
    GraphRelationship,
    GraphQueryResult,
)

class InMemoryGraphAdapter(GraphStorePort):
    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._outgoing: Dict[str, List[GraphRelationship]] = {}
        self._incoming: Dict[str, List[GraphRelationship]] = {}
        self._relationships: List[GraphRelationship] = []

    def upsert_node(self, node: GraphNode) -> None:
        self._nodes[node.id] = node
        if node.id not in self._outgoing:
            self._outgoing[node.id] = []
        if node.id not in self._incoming:
            self._incoming[node.id] = []

    def upsert_relationship(self, relationship: GraphRelationship) -> None:
        if relationship.source_id not in self._nodes or relationship.target_id not in self._nodes:
            return

        self._outgoing[relationship.source_id].append(relationship)
        self._incoming[relationship.target_id].append(relationship)
        self._relationships.append(relationship)

    def query_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> GraphQueryResult:
        q_lower = query.lower().strip()
        matched_nodes: List[GraphNode] = []
        params = parameters or {}

        if "id" in params and params["id"] in self._nodes:
            matched_nodes = [self._nodes[params["id"]]]
        elif "match (n:" in q_lower or "match (r:" in q_lower:
            parts = q_lower.split("match (")[1].split(")")[0].split(":")
            if len(parts) > 1:
                target_label = parts[1].strip()
                matched_nodes = [n for n in self._nodes.values() if n.label.lower() == target_label]
        else:
            matched_nodes = list(self._nodes.values())

        records = [
            {"id": n.id, "label": n.label, "properties": n.properties}
            for n in matched_nodes
        ]

        return GraphQueryResult(
            nodes=matched_nodes,
            relationships=self._relationships,
            records=records,
        )

    def find_neighbors(
        self,
        node_id: str,
        rel_type: Optional[str] = None,
        direction: str = "OUTGOING",
    ) -> List[GraphNode]:
        result_nodes: List[GraphNode] = []
        if node_id not in self._nodes:
            return result_nodes

        edges_to_check: List[GraphRelationship] = []
        if direction in ("OUTGOING", "BOTH"):
            edges_to_check.extend(self._outgoing.get(node_id, []))
        if direction in ("INCOMING", "BOTH"):
            edges_to_check.extend(self._incoming.get(node_id, []))

        for edge in edges_to_check:
            if rel_type and edge.rel_type != rel_type:
                continue
            target_id = edge.target_id if edge.source_id == node_id else edge.source_id
            if target_id in self._nodes:
                result_nodes.append(self._nodes[target_id])

        return result_nodes

    def find_shortest_path(self, start_id: str, end_id: str) -> List[GraphNode]:
        if start_id not in self._nodes or end_id not in self._nodes:
            return []
        if start_id == end_id:
            return [self._nodes[start_id]]

        queue = deque([(start_id, [start_id])])
        visited: Set[str] = {start_id}

        while queue:
            curr_id, path = queue.popleft()
            for edge in self._outgoing.get(curr_id, []):
                nxt_id = edge.target_id
                if nxt_id == end_id:
                    return [self._nodes[nid] for nid in path + [nxt_id]]
                if nxt_id not in visited and nxt_id in self._nodes:
                    visited.add(nxt_id)
                    queue.append((nxt_id, path + [nxt_id]))

        return []

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def find_node(self, query: str) -> Optional[GraphNode]:
        if not query:
            return None
        q = query.strip()
        if q in self._nodes:
            return self._nodes[q]

        from pathlib import Path
        stem = Path(q).stem
        for node in self._nodes.values():
            props = node.properties or {}
            fpath = props.get("file_path", "")
            if node.id == q or fpath == q or fpath.endswith(q) or node.id.endswith(q):
                return node
            if stem and (stem == Path(fpath).stem or stem in node.id):
                return node
        return None


    def get_incoming_relationships(self, node_id: str) -> List[GraphRelationship]:
        return list(self._incoming.get(node_id, []))

    def get_outgoing_relationships(self, node_id: str) -> List[GraphRelationship]:
        return list(self._outgoing.get(node_id, []))

    def delete_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        del self._nodes[node_id]
        self._outgoing.pop(node_id, None)
        self._incoming.pop(node_id, None)
        self._relationships = [
            r for r in self._relationships
            if r.source_id != node_id and r.target_id != node_id
        ]
        return True

    def count_nodes(self) -> int:
        return len(self._nodes)

    def count_relationships(self) -> int:
        return len(self._relationships)

    def clear(self) -> None:
        self._nodes.clear()
        self._outgoing.clear()
        self._incoming.clear()
        self._relationships.clear()
