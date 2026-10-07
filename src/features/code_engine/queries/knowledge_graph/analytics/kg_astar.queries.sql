-- ================================================================================
-- KNOWLEDGE GRAPH ANALYTICS: A* SHORTEST PATH NAMED QUERIES
-- ================================================================================
-- Rule 2.4 / 3.7: Named Parameterized Queries Formula FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- ================================================================================

-- name: FLOW_GET_PROJECTED_ASTAR_SHORTEST_PATH
MATCH (source {id: $source_id}), (target {id: $target_id})
CALL gds.shortestPath.astar.stream($graph_name, {
  sourceNode: source,
  targetNode: target,
  latitudeProperty: $latitude_prop,
  longitudeProperty: $longitude_prop,
  relationshipWeightProperty: $weight_prop
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN totalCost, [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS path;

-- name: FLOW_GET_PROCEDURE_ASTAR_SHORTEST_PATH
MATCH (start {id: $source_id}), (end {id: $target_id})
CALL apoc.algo.aStar(start, end, $rel_type, $weight_prop, $lat_prop, $lon_prop)
YIELD path, weight
RETURN weight AS totalCost, [n IN nodes(path) | n.id] AS path;
