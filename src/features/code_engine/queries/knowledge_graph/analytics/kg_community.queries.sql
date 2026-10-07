-- ================================================================================
-- KNOWLEDGE GRAPH ANALYTICS: COMMUNITY & PARTITIONING NAMED QUERIES
-- ================================================================================
-- Rule 2.4 / 3.7: Named Parameterized Queries Formula FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Native Neo4j Graph Data Science (GDS) & APOC Procedures
-- ================================================================================

-- name: FLOW_GET_PROJECTED_CONNECTED_COMPONENTS
CALL gds.wcc.stream($graph_name)
YIELD nodeId, componentId
RETURN gds.util.asNode(nodeId).id AS node_id, componentId AS component_id;

-- name: FLOW_GET_PROCEDURE_CONNECTED_COMPONENTS
CALL apoc.algo.community($iterations, [$label], 'partition', $rel_type, 'BOTH', 'weight', 10000)
YIELD node, community
RETURN node.id AS node_id, community AS component_id;

-- name: FLOW_GET_CONNECTED_COMPONENTS
CALL gds.wcc.stream($graph_name)
YIELD nodeId, componentId
RETURN gds.util.asNode(nodeId).id AS node_id, componentId AS component_id;

-- name: FLOW_GET_PROJECTED_STRONGLY_CONNECTED_COMPONENTS
CALL gds.scc.stream($graph_name)
YIELD nodeId, componentId
RETURN gds.util.asNode(nodeId).id AS node_id, componentId AS component_id;

-- name: FLOW_GET_STRONGLY_CONNECTED_COMPONENTS
CALL gds.scc.stream($graph_name)
YIELD nodeId, componentId
RETURN gds.util.asNode(nodeId).id AS node_id, componentId AS component_id;

-- name: FLOW_GET_PROJECTED_K_CORE_DECOMPOSITION
CALL gds.kcore.stream($graph_name, {
  k: $k
})
YIELD nodeId, coreValue
RETURN gds.util.asNode(nodeId).id AS node_id, coreValue AS core_value;

-- name: FLOW_GET_K_CORE_DECOMPOSITION
CALL gds.kcore.stream($graph_name, {
  k: $k
})
YIELD nodeId, coreValue
RETURN gds.util.asNode(nodeId).id AS node_id, coreValue AS core_value;

-- name: FLOW_GET_PROJECTED_LABEL_PROPAGATION
CALL gds.labelPropagation.stream($graph_name, {
  maxIterations: $max_iterations
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS node_id, communityId AS community_id;

-- name: FLOW_GET_LABEL_PROPAGATION
CALL gds.labelPropagation.stream($graph_name, {
  maxIterations: $max_iterations
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS node_id, communityId AS community_id;

-- name: FLOW_GET_PROJECTED_LOUVAIN_COMMUNITIES
CALL gds.louvain.stream($graph_name, {
  maxLevels: $max_levels,
  maxIterations: $max_iterations
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS node_id, communityId AS community_id;

-- name: FLOW_GET_LOUVAIN_COMMUNITIES
CALL gds.louvain.stream($graph_name, {
  maxLevels: $max_levels,
  maxIterations: $max_iterations
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS node_id, communityId AS community_id;

-- name: FLOW_GET_PROJECTED_LEIDEN_COMMUNITIES
CALL gds.leiden.stream($graph_name, {
  maxLevels: $max_levels,
  gamma: $gamma
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS node_id, communityId AS community_id;

-- name: FLOW_GET_LEIDEN_COMMUNITIES
CALL gds.leiden.stream($graph_name, {
  maxLevels: $max_levels,
  gamma: $gamma
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS node_id, communityId AS community_id;
