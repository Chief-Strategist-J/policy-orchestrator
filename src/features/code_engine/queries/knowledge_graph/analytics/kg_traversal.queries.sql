-- ================================================================================
-- KNOWLEDGE GRAPH ANALYTICS: TRAVERSAL & SHORTEST PATHS NAMED QUERIES
-- ================================================================================
-- Rule 2.4 / 3.7: Named Parameterized Queries Formula FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Native Neo4j Graph Data Science (GDS) & APOC Procedures
-- ================================================================================

-- name: FLOW_GET_PROJECTED_BFS_TRAVERSAL
MATCH (source {id: $start_node})
CALL gds.bfs.stream($graph_name, {
  sourceNode: source,
  targetNodes: $target_nodes
})
YIELD path
RETURN [n IN nodes(path) | n.id] AS visited_path, length(path) AS depth;

-- name: FLOW_GET_PROCEDURE_BFS_TRAVERSAL
MATCH (start {id: $start_node})
CALL apoc.path.expandConfig(start, {
  relationshipFilter: $rel_filter,
  minLevel: 1,
  maxLevel: $max_depth,
  bfs: true,
  uniqueness: 'NODE_GLOBAL'
})
YIELD path
RETURN [n IN nodes(path) | n.id] AS visited_path, length(path) AS depth;

-- name: FLOW_GET_BFS_TRAVERSAL
MATCH (start {id: $start_node})
CALL apoc.path.expandConfig(start, {
  relationshipFilter: $rel_filter,
  minLevel: 1,
  maxLevel: $max_depth,
  bfs: true,
  uniqueness: 'NODE_GLOBAL'
})
YIELD path
RETURN [n IN nodes(path) | n.id] AS visited_path, length(path) AS depth;

-- name: FLOW_GET_PROJECTED_DFS_TRAVERSAL
MATCH (source {id: $start_node})
CALL gds.dfs.stream($graph_name, {
  sourceNode: source,
  targetNodes: $target_nodes
})
YIELD path
RETURN [n IN nodes(path) | n.id] AS traversal_order;

-- name: FLOW_GET_PROCEDURE_DFS_TRAVERSAL
MATCH (start {id: $start_node})
CALL apoc.path.expandConfig(start, {
  relationshipFilter: $rel_filter,
  minLevel: 1,
  maxLevel: $max_depth,
  bfs: false,
  uniqueness: 'NODE_PATH'
})
YIELD path
RETURN [n IN nodes(path) | n.id] AS traversal_order;

-- name: FLOW_GET_DFS_TRAVERSAL
MATCH (start {id: $start_node})
CALL apoc.path.expandConfig(start, {
  relationshipFilter: $rel_filter,
  minLevel: 1,
  maxLevel: $max_depth,
  bfs: false,
  uniqueness: 'NODE_PATH'
})
YIELD path
RETURN [n IN nodes(path) | n.id] AS traversal_order;

-- name: FLOW_GET_PROJECTED_BIDIRECTIONAL_BFS_PATH
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL gds.shortestPath.dijkstra.stream($graph_name, {
  sourceNode: source,
  targetNode: target
})
YIELD index, totalCost, nodeIds, path
RETURN [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS path, totalCost AS total_cost;

-- name: FLOW_GET_PROCEDURE_BIDIRECTIONAL_BFS_PATH
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL apoc.algo.dijkstra(source, target, $rel_type, $weight_prop)
YIELD path, weight
RETURN [n IN nodes(path) | n.id] AS path, weight AS total_cost;

-- name: FLOW_GET_BIDIRECTIONAL_BFS_PATH
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL apoc.algo.dijkstra(source, target, $rel_type, $weight_prop)
YIELD path, weight
RETURN [n IN nodes(path) | n.id] AS path, weight AS total_cost;

-- name: FLOW_GET_PROJECTED_DIJKSTRA_SHORTEST_PATH
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL gds.shortestPath.dijkstra.stream($graph_name, {
  sourceNode: source,
  targetNode: target,
  relationshipWeightProperty: $weight_prop
})
YIELD index, totalCost, nodeIds, path
RETURN index, totalCost AS cost, [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS path;

-- name: FLOW_GET_PROCEDURE_DIJKSTRA_SHORTEST_PATH
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL apoc.algo.dijkstra(source, target, $rel_type, $weight_prop)
YIELD path, weight
RETURN [n IN nodes(path) | n.id] AS path, weight AS total_cost;

-- name: FLOW_GET_DIJKSTRA_SHORTEST_PATH
MATCH (source {id: $source_id})
CALL gds.allShortestPaths.dijkstra.stream($graph_name, {
  sourceNode: source,
  relationshipWeightProperty: $weight_prop
})
YIELD targetNode, totalCost
RETURN gds.util.asNode(targetNode).id AS target_id, totalCost AS distance;

-- name: FLOW_GET_PROJECTED_YENS_K_SHORTEST_PATHS
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL gds.shortestPath.yens.stream($graph_name, {
  sourceNode: source,
  targetNode: target,
  k: $k,
  relationshipWeightProperty: $weight_prop
})
YIELD index, totalCost, nodeIds, path
RETURN index AS rank, totalCost AS cost, [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS path;

-- name: FLOW_GET_PROCEDURE_YENS_K_SHORTEST_PATHS
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL apoc.algo.kShortestPaths(source, target, $k, $weight_prop)
YIELD path, weight
RETURN [n IN nodes(path) | n.id] AS path, weight AS cost;

-- name: FLOW_GET_YENS_K_SHORTEST_PATHS
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL gds.shortestPath.yens.stream($graph_name, {
  sourceNode: source,
  targetNode: target,
  k: $k,
  relationshipWeightProperty: $weight_prop
})
YIELD index, totalCost, nodeIds
RETURN index AS rank, totalCost AS cost, [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS path;
