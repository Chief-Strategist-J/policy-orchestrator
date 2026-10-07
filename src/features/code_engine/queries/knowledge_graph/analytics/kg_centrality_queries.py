"""
================================================================================
NAMED QUERIES CONSTANTS: KNOWLEDGE GRAPH CENTRALITY & PRESTIGE
================================================================================
Rule 2.4 / 3.7: FLOW_{VERB}_{ENTITY}_{CRITERIA}
Native Neo4j Graph Data Science (GDS) & APOC Procedures
================================================================================
"""

FLOW_GET_PROJECTED_PAGERANK_CENTRALITY: str = """
CALL gds.pageRank.stream($graph_name, {
  dampingFactor: $damping_factor,
  maxIterations: $max_iterations,
  tolerance: $tolerance
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score
""".strip()

FLOW_GET_PROCEDURE_PAGERANK_CENTRALITY: str = """
CALL apoc.algo.pageRankWithConfig($nodes, {
  iterations: $max_iterations,
  types: $rel_types
})
YIELD node, score
RETURN node.id AS node_id, score
""".strip()

FLOW_GET_PAGERANK_CENTRALITY: str = FLOW_GET_PROJECTED_PAGERANK_CENTRALITY

FLOW_GET_PROJECTED_PERSONALIZED_PAGERANK: str = """
MATCH (seed {id: $seed_node})
CALL gds.pageRank.stream($graph_name, {
  sourceNodes: [seed],
  dampingFactor: $damping_factor,
  maxIterations: $max_iterations
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score
""".strip()

FLOW_GET_PERSONALIZED_PAGERANK: str = FLOW_GET_PROJECTED_PERSONALIZED_PAGERANK

FLOW_GET_PROJECTED_DEGREE_CENTRALITY: str = """
CALL gds.degree.stream($graph_name, {
  orientation: $orientation
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score AS degree
""".strip()

FLOW_GET_DEGREE_CENTRALITY: str = """
MATCH (n)
RETURN n.id AS node_id, COUNT { (n)--() } AS degree
""".strip()

FLOW_GET_PROJECTED_HARMONIC_CLOSENESS: str = """
CALL gds.closeness.harmonic.stream($graph_name)
YIELD nodeId, centrality
RETURN gds.util.asNode(nodeId).id AS node_id, centrality AS score
""".strip()

FLOW_GET_PROJECTED_CLOSENESS_CENTRALITY: str = """
CALL gds.closeness.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score
""".strip()

FLOW_GET_PROCEDURE_CLOSENESS_CENTRALITY: str = """
CALL apoc.algo.closeness($rel_types, $nodes, 'BOTH')
YIELD node, score
RETURN node.id AS node_id, score
""".strip()

FLOW_GET_HARMONIC_CLOSENESS: str = FLOW_GET_PROJECTED_HARMONIC_CLOSENESS

FLOW_GET_PROJECTED_BETWEENNESS_CENTRALITY: str = """
CALL gds.betweenness.stream($graph_name)
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS node_id, score
""".strip()

FLOW_GET_PROCEDURE_BETWEENNESS_CENTRALITY: str = """
CALL apoc.algo.betweenness($rel_types, $nodes, 'BOTH')
YIELD node, score
RETURN node.id AS node_id, score
""".strip()

FLOW_GET_BETWEENNESS_CENTRALITY: str = FLOW_GET_PROJECTED_BETWEENNESS_CENTRALITY

FLOW_GET_PROJECTED_HITS_CENTRALITY: str = """
CALL gds.hits.stream($graph_name, {
  hitsIterations: $hits_iterations
})
YIELD nodeId, values
RETURN gds.util.asNode(nodeId).id AS node_id, values.auth AS auth_score, values.hub AS hub_score
""".strip()

FLOW_GET_HITS_CENTRALITY: str = FLOW_GET_PROJECTED_HITS_CENTRALITY

__all__ = [
    "FLOW_GET_PROJECTED_PAGERANK_CENTRALITY",
    "FLOW_GET_PROCEDURE_PAGERANK_CENTRALITY",
    "FLOW_GET_PAGERANK_CENTRALITY",
    "FLOW_GET_PROJECTED_PERSONALIZED_PAGERANK",
    "FLOW_GET_PERSONALIZED_PAGERANK",
    "FLOW_GET_PROJECTED_DEGREE_CENTRALITY",
    "FLOW_GET_DEGREE_CENTRALITY",
    "FLOW_GET_PROJECTED_HARMONIC_CLOSENESS",
    "FLOW_GET_PROJECTED_CLOSENESS_CENTRALITY",
    "FLOW_GET_PROCEDURE_CLOSENESS_CENTRALITY",
    "FLOW_GET_HARMONIC_CLOSENESS",
    "FLOW_GET_PROJECTED_BETWEENNESS_CENTRALITY",
    "FLOW_GET_PROCEDURE_BETWEENNESS_CENTRALITY",
    "FLOW_GET_BETWEENNESS_CENTRALITY",
    "FLOW_GET_PROJECTED_HITS_CENTRALITY",
    "FLOW_GET_HITS_CENTRALITY",
]
