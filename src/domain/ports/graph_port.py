"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH KNOWLEDGE STORE PORT (HEXAGONAL)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port for Graph Knowledge
   Databases (Neo4j, Memgraph, FalkorDB, Amazon Neptune, In-Memory Graph).
   It enables semantic knowledge graphs over policy rules, architectural
   invariants, service dependencies, and security boundaries.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All graph data structures, traversal contracts,
     and Cypher/GQL query abstractions are documented in this header.
     Interface declarations remain 100% comment-free and pure.
   - Property Graph Model: Supports labeled nodes with arbitrary property maps
     and directed typed relationships with weights/attributes.
   - Cypher / OpenGraph Query Abstraction: Enables expressive pattern matching
     (e.g., `MATCH (r:Rule)-[:VIOLATES]->(s:Service)`).

3. METHOD CONTRACTS:
   - upsert_node(): Inserts or updates an entity node in the graph.
   - upsert_relationship(): Establishes directed typed edge between two nodes.
   - query_cypher(): Executes declarative Cypher pattern matching queries.
   - find_neighbors(): Retrieves adjacent connected nodes filtered by relation type.
   - find_shortest_path(): Computes minimal graph path between source and target.
   - clear(): Resets graph workspace.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GraphRelationship:
    source_id: str
    target_id: str
    rel_type: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GraphQueryResult:
    nodes: List[GraphNode] = field(default_factory=list)
    relationships: List[GraphRelationship] = field(default_factory=list)
    records: List[Dict[str, Any]] = field(default_factory=list)

class GraphStorePort(ABC):
    @abstractmethod
    def upsert_node(self, node: GraphNode) -> None:
        pass

    @abstractmethod
    def upsert_relationship(self, relationship: GraphRelationship) -> None:
        pass

    @abstractmethod
    def query_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> GraphQueryResult:
        pass

    @abstractmethod
    def find_neighbors(
        self,
        node_id: str,
        rel_type: Optional[str] = None,
        direction: str = "OUTGOING"
    ) -> List[GraphNode]:
        pass

    @abstractmethod
    def find_shortest_path(self, start_id: str, end_id: str) -> List[GraphNode]:
        pass

    @abstractmethod
    def count_nodes(self) -> int:
        pass

    @abstractmethod
    def count_relationships(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
