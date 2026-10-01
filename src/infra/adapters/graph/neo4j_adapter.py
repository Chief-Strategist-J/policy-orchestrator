"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NEO4J / MEMGRAPH KNOWLEDGE GRAPH ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements GraphStorePort for Neo4j and Memgraph graph databases
   using standard Cypher transactional HTTP API endpoints (`/db/neo4j/tx/commit`).
   It provides open-standard graph storage without proprietary client SDKs.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: HTTP header generation, Cypher statement
     serialization, parameter binding, and result unpacking are in this blueprint.
     Class methods are 100% comment-free and pure.
   - Dual-Mode Resilience: If connection to remote Neo4j/Memgraph fails, errors
     are cleanly surfaced to the caller.

3. METHOD CONTRACTS:
   - upsert_node(): `MERGE (n:Label {id: $id}) SET n += $props`
   - upsert_relationship(): `MATCH (a {id: $src}), (b {id: $tgt}) MERGE (a)-[r:REL]->(b)`
   - query_cypher(): Executes arbitrary Cypher query against transactional endpoint.
================================================================================
"""

import json
import base64
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

from src.domain.ports.graph_port import (
    GraphStorePort,
    GraphNode,
    GraphRelationship,
    GraphQueryResult,
)

class Neo4jGraphAdapter(GraphStorePort):
    def __init__(
        self,
        uri: str = "http://localhost:7474",
        user: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
        timeout: int = 30,
    ) -> None:
        self.endpoint = f"{uri.rstrip('/')}/db/{database}/tx/commit"
        self.user = user
        self.password = password
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
        cypher = (
            "MATCH p = shortestPath((a {id: $start})-[*..15]->(b {id: $end})) "
            "RETURN [n in nodes(p) | {id: n.id, label: labels(n)[0], props: properties(n)}] as path"
        )
        res = self.query_cypher(cypher, {"start": start_id, "end": end_id})
        if not res.records or not res.records[0].get("path"):
            return []
        raw_path = res.records[0]["path"]
        return [
            GraphNode(
                id=str(item.get("id")),
                label=str(item.get("label") or "Entity"),
                properties=item.get("props") or {},
            )
            for item in raw_path
        ]

    def count_nodes(self) -> int:
        res = self.query_cypher("MATCH (n) RETURN count(n) as total")
        return int(res.records[0]["total"]) if res.records else 0

    def count_relationships(self) -> int:
        res = self.query_cypher("MATCH ()-[r]->() RETURN count(r) as total")
        return int(res.records[0]["total"]) if res.records else 0

    def clear(self) -> None:
        self._execute_statements([{"statement": "MATCH (n) DETACH DELETE n"}])
