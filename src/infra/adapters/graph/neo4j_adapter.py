"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NEO4J KNOWLEDGE GRAPH ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements GraphStorePort for Neo4j graph databases using
   standard Cypher transactional HTTP API endpoints (/db/neo4j/tx/commit).
   It provides open-standard graph storage without proprietary client SDKs.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: HTTP header generation, Cypher statement
     serialization, parameter binding, and result unpacking are in this blueprint.
     Class methods are 100% comment-free and pure.
   - Dual-Mode Resilience: If connection to remote Neo4j fails, errors
     are cleanly surfaced to the caller.

3. METHOD CONTRACTS:
   - upsert_node(): MERGE (n:Label {id: $id}) SET n += $props
   - upsert_relationship(): MATCH (a {id: $src}), (b {id: $tgt}) MERGE (a)-[r:REL]->(b)
   - get_node(): Fetches single node by unique id.
   - get_incoming_relationships(): Fetches incoming edges for a node.
   - get_outgoing_relationships(): Fetches outgoing edges for a node.
   - delete_node(): Removes node and detached relationships.
   - query_cypher(): Executes arbitrary Cypher query against transactional endpoint.
================================================================================
"""

import json
import base64
import os
import urllib.request
import urllib.error
from collections import deque
from typing import List, Dict, Any, Optional, Set

from src.domain.ports.graph_port import (
    GraphStorePort,
    GraphNode,
    GraphRelationship,
    GraphQueryResult,
)

class Neo4jGraphAdapter(GraphStorePort):
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j",
        timeout: int = 30,
    ) -> None:
        raw_uri = uri or os.environ.get("NEO4J_URI", "http://localhost:7474")
        self.endpoint = f"{raw_uri.rstrip('/')}/db/{database}/tx/commit"
        self.user = user or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "policysecret")
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        auth_str = f"{self.user}:{self.password}"
        encoded_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_auth}",
        }

    def _execute_statements(self, statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        payload = {"statements": statements}
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._get_headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                errors = data.get("errors", [])
                if errors:
                    raise RuntimeError(f"Neo4j Cypher Error: {errors[0].get('message')}")
                return data
        except Exception as exc:
            raise RuntimeError(f"Neo4j HTTP connection failure: {str(exc)}") from exc

    def upsert_node(self, node: GraphNode) -> None:
        cypher = f"MERGE (n:{node.label} {{id: $id}}) SET n += $props"
        self._execute_statements([{"statement": cypher, "parameters": {"id": node.id, "props": node.properties}}])

    def upsert_relationship(self, relationship: GraphRelationship) -> None:
        cypher = (
            f"MATCH (a {{id: $src}}), (b {{id: $tgt}}) "
            f"MERGE (a)-[r:{relationship.rel_type}]->(b) "
            f"SET r += $props"
        )
        self._execute_statements(
            [
                {
                    "statement": cypher,
                    "parameters": {
                        "src": relationship.source_id,
                        "tgt": relationship.target_id,
                        "props": relationship.properties,
                    },
                }
            ]
        )

    def query_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> GraphQueryResult:
        res = self._execute_statements([{"statement": query, "parameters": parameters or {}}])
        results_data = res.get("results", [{}])[0]
        columns = results_data.get("columns", [])
        data_rows = results_data.get("data", [])

        records: List[Dict[str, Any]] = []
        for row in data_rows:
            row_vals = row.get("row", [])
            records.append({col: row_vals[idx] if idx < len(row_vals) else None for idx, col in enumerate(columns)})

        return GraphQueryResult(nodes=[], relationships=[], records=records)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        cypher = "MATCH (n {id: $id}) RETURN n.id as id, labels(n)[0] as label, properties(n) as props LIMIT 1"
        res = self.query_cypher(cypher, {"id": node_id})
        if not res.records:
            return None
        r = res.records[0]
        return GraphNode(
            id=str(r.get("id")),
            label=str(r.get("label") or "Entity"),
            properties=r.get("props") or {},
        )

    def find_node(self, query: str) -> Optional[GraphNode]:
        if not query:
            return None
        q = query.strip()
        from pathlib import Path
        stem = Path(q).stem
        cypher = """
        MATCH (n)
        WHERE n.id = $q
           OR n.file_path = $q
           OR n.file_path ENDS WITH $q
           OR n.id ENDS WITH $q
           OR n.id CONTAINS $stem
           OR n.file_path CONTAINS $stem
        RETURN n.id AS id, labels(n)[0] AS label, properties(n) AS props
        LIMIT 1
        """
        res = self.query_cypher(cypher, {"q": q, "stem": stem})
        if not res.records:
            return None
        r = res.records[0]
        return GraphNode(
            id=str(r.get("id")),
            label=str(r.get("label") or "Entity"),
            properties=r.get("props") or {},
        )


    def get_incoming_relationships(self, node_id: str) -> List[GraphRelationship]:
        cypher = "MATCH (s)-[r]->(t {id: $id}) RETURN s.id as src, type(r) as rel_type, t.id as tgt, properties(r) as props"
        res = self.query_cypher(cypher, {"id": node_id})
        return [
            GraphRelationship(
                source_id=str(r.get("src")),
                target_id=str(r.get("tgt")),
                rel_type=str(r.get("rel_type")),
                properties=r.get("props") or {},
            )
            for r in res.records
        ]

    def get_outgoing_relationships(self, node_id: str) -> List[GraphRelationship]:
        cypher = "MATCH (s {id: $id})-[r]->(t) RETURN s.id as src, type(r) as rel_type, t.id as tgt, properties(r) as props"
        res = self.query_cypher(cypher, {"id": node_id})
        return [
            GraphRelationship(
                source_id=str(r.get("src")),
                target_id=str(r.get("tgt")),
                rel_type=str(r.get("rel_type")),
                properties=r.get("props") or {},
            )
            for r in res.records
        ]

    def delete_node(self, node_id: str) -> bool:
        cypher = "MATCH (n {id: $id}) DETACH DELETE n"
        res = self.query_cypher("MATCH (n {id: $id}) RETURN count(n) as cnt", {"id": node_id})
        cnt = int(res.records[0]["cnt"]) if res.records else 0
        if cnt == 0:
            return False
        self._execute_statements([{"statement": cypher, "parameters": {"id": node_id}}])
        return True

    def find_neighbors(
        self,
        node_id: str,
        rel_type: Optional[str] = None,
        direction: str = "OUTGOING",
    ) -> List[GraphNode]:
        rel_clause = f":{rel_type}" if rel_type else ""
        if direction == "OUTGOING":
            cypher = f"MATCH (n {{id: $id}})-[r{rel_clause}]->(m) RETURN m.id as id, labels(m)[0] as label, properties(m) as props"
        elif direction == "INCOMING":
            cypher = f"MATCH (n {{id: $id}})<-[r{rel_clause}]-(m) RETURN m.id as id, labels(m)[0] as label, properties(m) as props"
        else:
            cypher = f"MATCH (n {{id: $id}})-[r{rel_clause}]-(m) RETURN m.id as id, labels(m)[0] as label, properties(m) as props"

        res = self.query_cypher(cypher, {"id": node_id})
        return [
            GraphNode(
                id=str(r.get("id")),
                label=str(r.get("label") or "Entity"),
                properties=r.get("props") or {},
            )
            for r in res.records
        ]

    def find_shortest_path(self, start_id: str, end_id: str) -> List[GraphNode]:
        if start_id == end_id:
            node = self.get_node(start_id)
            return [node] if node else []

        queue = deque([(start_id, [start_id])])
        visited: Set[str] = {start_id}

        while queue:
            curr_id, path = queue.popleft()
            neighbors = self.find_neighbors(curr_id, direction="OUTGOING")
            for neighbor in neighbors:
                if neighbor.id == end_id:
                    path_nodes: List[GraphNode] = []
                    for nid in path + [neighbor.id]:
                        n = self.get_node(nid)
                        if n:
                            path_nodes.append(n)
                    return path_nodes
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, path + [neighbor.id]))

        return []

    def count_nodes(self) -> int:
        res = self.query_cypher("MATCH (n) RETURN count(n) as total")
        return int(res.records[0]["total"]) if res.records else 0

    def count_relationships(self) -> int:
        res = self.query_cypher("MATCH ()-[r]->() RETURN count(r) as total")
        return int(res.records[0]["total"]) if res.records else 0

    def clear(self) -> None:
        self._execute_statements([{"statement": "MATCH (n) DETACH DELETE n"}])
