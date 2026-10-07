-- ================================================================================
-- KNOWLEDGE GRAPH ANALYTICS: REACHABILITY & SAMPLING NAMED QUERIES
-- ================================================================================
-- Rule 2.4 / 3.7: Named Parameterized Queries Formula FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Native Neo4j Graph Data Science (GDS) & APOC Procedures
-- ================================================================================

-- name: FLOW_GET_PROJECTED_RANDOM_WALK_RESTART
MATCH (source {id: $start_node})
CALL gds.randomWalk.stream($graph_name, {
  sourceNodes: [source],
  walkLength: $walk_length,
  walksPerNode: $walks_per_node,
  restartProbability: $restart_probability
})
YIELD nodeIds
RETURN nodeIds AS walk_path;

-- name: FLOW_GET_RANDOM_WALK_RESTART
MATCH (source {id: $start_node})
CALL gds.randomWalk.stream($graph_name, {
  sourceNodes: [source],
  walkLength: $walk_length,
  walksPerNode: $walks_per_node,
  restartProbability: $restart_probability
})
YIELD nodeIds
RETURN nodeIds AS walk_path;

-- name: FLOW_GET_PROCEDURE_METAPATH_TRAVERSAL
MATCH (start {id: $start_node})
CALL apoc.path.expandConfig(start, {
  relationshipFilter: $rel_filter,
  minLevel: 1,
  maxLevel: $max_hops,
  bfs: true
})
YIELD path
RETURN [node IN nodes(path) | node.id] AS node_path;

-- name: FLOW_GET_PATTERN_METAPATH_TRAVERSAL
MATCH p = (start {id: $start_node})-[r*1..$max_hops]->(target)
WHERE [rel IN relationships(p) | type(rel)] = $metapath
RETURN DISTINCT target.id AS target_id;

-- name: FLOW_GET_METAPATH_TRAVERSAL
MATCH p = (start {id: $start_node})-[r*1..$max_hops]->(target)
WHERE [rel IN relationships(p) | type(rel)] = $metapath
RETURN DISTINCT target.id AS target_id;

-- name: FLOW_GET_PROCEDURE_TWO_HOP_REACHABILITY
MATCH (u {id: $source_id}), (v {id: $target_id})
CALL apoc.path.spanningTree(u, {
  minLevel: 2,
  maxLevel: 2,
  endNodes: [v]
})
YIELD path
RETURN count(path) > 0 AS is_reachable;

-- name: FLOW_GET_PATTERN_TWO_HOP_REACHABILITY
MATCH (u {id: $source_id})-[r1]->(hub)-[r2]->(v {id: $target_id})
RETURN count(hub) > 0 AS is_reachable;

-- name: FLOW_GET_TWO_HOP_REACHABILITY
MATCH (u {id: $source_id})-[r1]->(hub)-[r2]->(v {id: $target_id})
RETURN count(hub) > 0 AS is_reachable;

-- name: FLOW_GET_PROCEDURE_TRANSITIVE_CLOSURE
MATCH (start {id: $source_id})
CALL apoc.path.subgraphNodes(start, {
  maxLevel: $max_depth
})
YIELD node
RETURN DISTINCT node.id AS reachable_id;

-- name: FLOW_GET_PATTERN_TRANSITIVE_CLOSURE
MATCH (u {id: $source_id})-[*1..$max_depth]->(v)
RETURN DISTINCT u.id AS source_id, v.id AS reachable_id;

-- name: FLOW_GET_TRANSITIVE_CLOSURE
MATCH (u {id: $source_id})-[*1..$max_depth]->(v)
RETURN DISTINCT u.id AS source_id, v.id AS reachable_id;
