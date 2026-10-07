-- ================================================================================
-- KNOWLEDGE GRAPH ANALYTICS: CENTRALITY & PRESTIGE NAMED QUERIES
-- ================================================================================
-- Rule 2.4 / 3.7: Named Parameterized Queries Formula FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Native Neo4j Graph Data Science (GDS) & APOC Procedures
-- ================================================================================

-- name: FLOW_GET_PROJECTED_PAGERANK_CENTRALITY
CALL gds.pageRank.stream($graph_name, {
  dampingFactor: $damping_factor,
  maxIterations: $max_iterations,
  tolerance: $tolerance
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score;

-- name: FLOW_GET_PROCEDURE_PAGERANK_CENTRALITY
CALL apoc.algo.pageRankWithConfig($nodes, {
  iterations: $max_iterations,
  types: $rel_types
})
YIELD node, score
RETURN node.id AS node_id, score;

-- name: FLOW_GET_PAGERANK_CENTRALITY
CALL gds.pageRank.stream($graph_name, {
  dampingFactor: $damping_factor,
  maxIterations: $max_iterations,
  tolerance: $tolerance
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score;

-- name: FLOW_GET_PROJECTED_PERSONALIZED_PAGERANK
MATCH (seed {id: $seed_node})
CALL gds.pageRank.stream($graph_name, {
  sourceNodes: [seed],
  dampingFactor: $damping_factor,
  maxIterations: $max_iterations
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score;

-- name: FLOW_GET_PERSONALIZED_PAGERANK
MATCH (seed {id: $seed_node})
CALL gds.pageRank.stream($graph_name, {
  sourceNodes: [seed],
  dampingFactor: $damping_factor,
  maxIterations: $max_iterations
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score;

-- name: FLOW_GET_PROJECTED_DEGREE_CENTRALITY
CALL gds.degree.stream($graph_name, {
  orientation: $orientation
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS degree;

-- name: FLOW_GET_DEGREE_CENTRALITY
CALL gds.degree.stream($graph_name, {
  orientation: $orientation
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS degree;

-- name: FLOW_GET_PROJECTED_HARMONIC_CLOSENESS
CALL gds.closeness.harmonic.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS harmonic_score;

-- name: FLOW_GET_PROJECTED_CLOSENESS_CENTRALITY
CALL gds.closeness.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS closeness_score;

-- name: FLOW_GET_PROCEDURE_CLOSENESS_CENTRALITY
CALL apoc.algo.closeness($rel_types, $nodes, 'BOTH')
YIELD node, score
RETURN node.id AS node_id, score;

-- name: FLOW_GET_HARMONIC_CLOSENESS
CALL gds.closeness.harmonic.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS harmonic_score;

-- name: FLOW_GET_PROJECTED_BETWEENNESS_CENTRALITY
CALL gds.betweenness.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS betweenness_score;

-- name: FLOW_GET_PROCEDURE_BETWEENNESS_CENTRALITY
CALL apoc.algo.betweenness($rel_types, $nodes, 'BOTH')
YIELD node, score
RETURN node.id AS node_id, score;

-- name: FLOW_GET_BETWEENNESS_CENTRALITY
CALL gds.betweenness.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS betweenness_score;

-- name: FLOW_GET_PROJECTED_HITS_CENTRALITY
CALL gds.hits.stream($graph_name, {
  hitsIterations: $iterations
})
YIELD nodeId, hub, auth
RETURN gds.util.asNode(nodeId).id AS node_id, hub AS hub_score, auth AS auth_score;

-- name: FLOW_GET_HITS_CENTRALITY
CALL gds.hits.stream($graph_name, {
  hitsIterations: $iterations
})
YIELD nodeId, hub, auth
RETURN gds.util.asNode(nodeId).id AS node_id, hub AS hub_score, auth AS auth_score;
