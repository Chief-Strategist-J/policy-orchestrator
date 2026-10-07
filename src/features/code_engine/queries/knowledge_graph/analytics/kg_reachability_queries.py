"""
================================================================================
NAMED QUERIES CONSTANTS: KNOWLEDGE GRAPH REACHABILITY & WALK SAMPLING
================================================================================
Rule 2.4 / 3.7: FLOW_{VERB}_{ENTITY}_{CRITERIA}
Native Neo4j Graph Data Science (GDS) & APOC Procedures
================================================================================
"""

FLOW_GET_PROJECTED_RANDOM_WALK_RESTART: str = """
MATCH (source {id: $start_node})
CALL gds.randomWalk.stream($graph_name, {
  sourceNodes: [source],
  walkLength: $walk_length,
  walksPerNode: $walks_per_node,
  restartProbability: $restart_probability
})
YIELD nodeIds
RETURN nodeIds AS walk_path
""".strip()

FLOW_GET_RANDOM_WALK_RESTART: str = FLOW_GET_PROJECTED_RANDOM_WALK_RESTART

FLOW_GET_PROCEDURE_METAPATH_TRAVERSAL: str = """
MATCH (start {id: $start_node})
CALL apoc.path.expandConfig(start, {
  relationshipFilter: $rel_filter,
  minLevel: 1,
  maxLevel: $max_hops,
  bfs: true
})
YIELD path
RETURN [node IN nodes(path) | node.id] AS node_path
""".strip()

FLOW_GET_PATTERN_METAPATH_TRAVERSAL: str = """
MATCH p = (start {id: $start_node})-[r*1..$max_hops]->(target)
WHERE [rel IN relationships(p) | type(rel)] = $metapath
RETURN DISTINCT target.id AS target_id
""".strip()

FLOW_GET_METAPATH_TRAVERSAL: str = FLOW_GET_PATTERN_METAPATH_TRAVERSAL

FLOW_GET_PROCEDURE_TWO_HOP_REACHABILITY: str = """
MATCH (u {id: $source_id}), (v {id: $target_id})
CALL apoc.path.spanningTree(u, {
  minLevel: 2,
  maxLevel: 2,
  endNodes: [v]
})
YIELD path
RETURN count(path) > 0 AS is_reachable
""".strip()

FLOW_GET_PATTERN_TWO_HOP_REACHABILITY: str = """
MATCH (u {id: $source_id})-[r1]->(hub)-[r2]->(v {id: $target_id})
RETURN count(hub) > 0 AS is_reachable
""".strip()

FLOW_GET_TWO_HOP_REACHABILITY: str = FLOW_GET_PATTERN_TWO_HOP_REACHABILITY

FLOW_GET_PROCEDURE_TRANSITIVE_CLOSURE: str = """
MATCH (source {id: $source_id})
CALL apoc.path.subgraphNodes(source, {
  minLevel: 1,
  maxLevel: $max_depth
})
YIELD node
RETURN collect(distinct node.id) AS reachable_nodes
""".strip()

FLOW_GET_PATTERN_TRANSITIVE_CLOSURE: str = """
MATCH (source {id: $source_id})-[r*1..$max_depth]->(target)
RETURN collect(distinct target.id) AS reachable_nodes
""".strip()

FLOW_GET_TRANSITIVE_CLOSURE: str = FLOW_GET_PATTERN_TRANSITIVE_CLOSURE

__all__ = [
    "FLOW_GET_PROJECTED_RANDOM_WALK_RESTART",
    "FLOW_GET_RANDOM_WALK_RESTART",
    "FLOW_GET_PROCEDURE_METAPATH_TRAVERSAL",
    "FLOW_GET_PATTERN_METAPATH_TRAVERSAL",
    "FLOW_GET_METAPATH_TRAVERSAL",
    "FLOW_GET_PROCEDURE_TWO_HOP_REACHABILITY",
    "FLOW_GET_PATTERN_TWO_HOP_REACHABILITY",
    "FLOW_GET_TWO_HOP_REACHABILITY",
    "FLOW_GET_PROCEDURE_TRANSITIVE_CLOSURE",
    "FLOW_GET_PATTERN_TRANSITIVE_CLOSURE",
    "FLOW_GET_TRANSITIVE_CLOSURE",
]
