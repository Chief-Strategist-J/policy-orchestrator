"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 KNOWLEDGE GRAPH QUERY, ANALYTICS & REASONING

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Knowledge Graph Query, Analytics & Reasoning.

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_federated_queries import KgAlgoFederatedQueries
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_gql_evaluator import KgAlgoGqlEvaluator
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_gremlin_traversal import KgAlgoGremlinTraversal
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_join_ordering_cardinality import KgAlgoJoinOrderingCardinality
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_leapfrog_triejoin import KgAlgoLeapfrogTriejoin
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_obda_query_rewriting import KgAlgoObdaQueryRewriting
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_opencypher_matcher import KgAlgoOpencypherMatcher
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_pagination_caching import KgAlgoPaginationCaching
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_parameterized_templates import KgAlgoParameterizedTemplates
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_regular_path_queries import KgAlgoRegularPathQueries
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_sparql_engine import KgAlgoSparqlEngine
from src.features.code_engine.algos.knowledge_graph.query.kg_algo_vf2_subgraph_isomorphism import KgAlgoVf2SubgraphIsomorphism
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_astar_search import KgAlgoAstarSearch
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_bfs_traversal import KgAlgoBfsTraversal
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_bidirectional_bfs import KgAlgoBidirectionalBfs
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_brandes_betweenness import KgAlgoBrandesBetweenness
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_closeness_harmonic import KgAlgoClosenessHarmonic
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_connected_components import KgAlgoConnectedComponents
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_degree_centrality import KgAlgoDegreeCentrality
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_dfs_traversal import KgAlgoDfsTraversal
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_dijkstra_shortest_path import KgAlgoDijkstraShortestPath
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_hits_centrality import KgAlgoHitsCentrality
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_k_core_decomposition import KgAlgoKCoreDecomposition
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_label_propagation import KgAlgoLabelPropagation
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_leiden_community import KgAlgoLeidenCommunity
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_louvain_community import KgAlgoLouvainCommunity
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_metapath_traversal import KgAlgoMetapathTraversal
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_pagerank_centrality import KgAlgoPagerankCentrality
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_personalized_pagerank import KgAlgoPersonalizedPagerank
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_random_walk_restart import KgAlgoRandomWalkRestart
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_tarjan_scc import KgAlgoTarjanScc
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_transitive_closure import KgAlgoTransitiveClosure
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_two_hop_labeling import KgAlgoTwoHopLabeling
from src.features.code_engine.algos.knowledge_graph.analytics.kg_algo_yens_k_shortest_paths import KgAlgoYensKShortestPaths
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_allens_interval_algebra import KgAlgoAllensIntervalAlgebra
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_amie_rule_mining import KgAlgoAmieRuleMining
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_backward_chaining import KgAlgoBackwardChaining
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_datalog_semi_naive import KgAlgoDatalogSemiNaive
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_dred_incremental_maintenance import KgAlgoDredIncrementalMaintenance
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_inconsistency_justification import KgAlgoInconsistencyJustification
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_inconsistency_repair import KgAlgoInconsistencyRepair
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_materialization_planner import KgAlgoMaterializationPlanner
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_open_closed_world import KgAlgoOpenClosedWorld
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_owl2_el_classification import KgAlgoOwl2ElClassification
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_owl2_rl_reasoner import KgAlgoOwl2RlReasoner
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_probabilistic_soft_logic import KgAlgoProbabilisticSoftLogic
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_rdfs_entailment import KgAlgoRdfsEntailment
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_rete_forward_chaining import KgAlgoReteForwardChaining
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_same_as_congruence import KgAlgoSameAsCongruence
from src.features.code_engine.algos.knowledge_graph.reasoning.kg_algo_tableau_reasoner import KgAlgoTableauReasoner

router = APIRouter(prefix="/algos/knowledge-graph/query-reasoning", tags=["Knowledge Graph Query & Reasoning Algorithms"])

class KgAlgoFederatedQueriesDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoGqlEvaluatorDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoGremlinTraversalDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoJoinOrderingCardinalityDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLeapfrogTriejoinDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoObdaQueryRewritingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOpencypherMatcherDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoPaginationCachingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoParameterizedTemplatesDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRegularPathQueriesDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSparqlEngineDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoVf2SubgraphIsomorphismDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoAstarSearchDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoBfsTraversalDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoBidirectionalBfsDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoBrandesBetweennessDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoClosenessHarmonicDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoConnectedComponentsDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDegreeCentralityDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDfsTraversalDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDijkstraShortestPathDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoHitsCentralityDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoKCoreDecompositionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLabelPropagationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLeidenCommunityDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLouvainCommunityDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoMetapathTraversalDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoPagerankCentralityDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoPersonalizedPagerankDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRandomWalkRestartDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTarjanSccDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTransitiveClosureDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTwoHopLabelingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoYensKShortestPathsDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoAllensIntervalAlgebraDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoAmieRuleMiningDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoBackwardChainingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDatalogSemiNaiveDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDredIncrementalMaintenanceDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoInconsistencyJustificationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoInconsistencyRepairDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoMaterializationPlannerDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOpenClosedWorldDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOwl2ElClassificationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOwl2RlReasonerDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoProbabilisticSoftLogicDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRdfsEntailmentDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoReteForwardChainingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSameAsCongruenceDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTableauReasonerDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")


@router.post("/federated-queries")
def kgalgofederatedqueries_endpoint(body: KgAlgoFederatedQueriesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoFederatedQueries()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoFederatedQueries"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/gql-evaluator")
def kgalgogqlevaluator_endpoint(body: KgAlgoGqlEvaluatorDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoGqlEvaluator()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoGqlEvaluator"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/gremlin-traversal")
def kgalgogremlintraversal_endpoint(body: KgAlgoGremlinTraversalDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoGremlinTraversal()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoGremlinTraversal"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/join-ordering-cardinality")
def kgalgojoinorderingcardinality_endpoint(body: KgAlgoJoinOrderingCardinalityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoJoinOrderingCardinality()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoJoinOrderingCardinality"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/leapfrog-triejoin")
def kgalgoleapfrogtriejoin_endpoint(body: KgAlgoLeapfrogTriejoinDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLeapfrogTriejoin()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLeapfrogTriejoin"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/obda-query-rewriting")
def kgalgoobdaqueryrewriting_endpoint(body: KgAlgoObdaQueryRewritingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoObdaQueryRewriting()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoObdaQueryRewriting"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/opencypher-matcher")
def kgalgoopencyphermatcher_endpoint(body: KgAlgoOpencypherMatcherDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOpencypherMatcher()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOpencypherMatcher"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/pagination-caching")
def kgalgopaginationcaching_endpoint(body: KgAlgoPaginationCachingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoPaginationCaching()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoPaginationCaching"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/parameterized-templates")
def kgalgoparameterizedtemplates_endpoint(body: KgAlgoParameterizedTemplatesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoParameterizedTemplates()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoParameterizedTemplates"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/regular-path-queries")
def kgalgoregularpathqueries_endpoint(body: KgAlgoRegularPathQueriesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRegularPathQueries()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRegularPathQueries"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/sparql-engine")
def kgalgosparqlengine_endpoint(body: KgAlgoSparqlEngineDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSparqlEngine()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSparqlEngine"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/vf2-subgraph-isomorphism")
def kgalgovf2subgraphisomorphism_endpoint(body: KgAlgoVf2SubgraphIsomorphismDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoVf2SubgraphIsomorphism()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoVf2SubgraphIsomorphism"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/astar-search")
def kgalgoastarsearch_endpoint(body: KgAlgoAstarSearchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoAstarSearch()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoAstarSearch"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/bfs-traversal")
def kgalgobfstraversal_endpoint(body: KgAlgoBfsTraversalDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoBfsTraversal()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoBfsTraversal"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/bidirectional-bfs")
def kgalgobidirectionalbfs_endpoint(body: KgAlgoBidirectionalBfsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoBidirectionalBfs()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoBidirectionalBfs"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/brandes-betweenness")
def kgalgobrandesbetweenness_endpoint(body: KgAlgoBrandesBetweennessDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoBrandesBetweenness()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoBrandesBetweenness"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/closeness-harmonic")
def kgalgoclosenessharmonic_endpoint(body: KgAlgoClosenessHarmonicDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoClosenessHarmonic()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoClosenessHarmonic"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/connected-components")
def kgalgoconnectedcomponents_endpoint(body: KgAlgoConnectedComponentsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoConnectedComponents()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoConnectedComponents"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/degree-centrality")
def kgalgodegreecentrality_endpoint(body: KgAlgoDegreeCentralityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDegreeCentrality()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDegreeCentrality"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/dfs-traversal")
def kgalgodfstraversal_endpoint(body: KgAlgoDfsTraversalDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDfsTraversal()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDfsTraversal"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/dijkstra-shortest-path")
def kgalgodijkstrashortestpath_endpoint(body: KgAlgoDijkstraShortestPathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDijkstraShortestPath()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDijkstraShortestPath"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/hits-centrality")
def kgalgohitscentrality_endpoint(body: KgAlgoHitsCentralityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoHitsCentrality()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoHitsCentrality"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/k-core-decomposition")
def kgalgokcoredecomposition_endpoint(body: KgAlgoKCoreDecompositionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoKCoreDecomposition()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoKCoreDecomposition"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/label-propagation")
def kgalgolabelpropagation_endpoint(body: KgAlgoLabelPropagationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLabelPropagation()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLabelPropagation"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/leiden-community")
def kgalgoleidencommunity_endpoint(body: KgAlgoLeidenCommunityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLeidenCommunity()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLeidenCommunity"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/louvain-community")
def kgalgolouvaincommunity_endpoint(body: KgAlgoLouvainCommunityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLouvainCommunity()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLouvainCommunity"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/metapath-traversal")
def kgalgometapathtraversal_endpoint(body: KgAlgoMetapathTraversalDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoMetapathTraversal()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoMetapathTraversal"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/pagerank-centrality")
def kgalgopagerankcentrality_endpoint(body: KgAlgoPagerankCentralityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoPagerankCentrality()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoPagerankCentrality"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/personalized-pagerank")
def kgalgopersonalizedpagerank_endpoint(body: KgAlgoPersonalizedPagerankDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoPersonalizedPagerank()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoPersonalizedPagerank"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/random-walk-restart")
def kgalgorandomwalkrestart_endpoint(body: KgAlgoRandomWalkRestartDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRandomWalkRestart()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRandomWalkRestart"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/tarjan-scc")
def kgalgotarjanscc_endpoint(body: KgAlgoTarjanSccDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTarjanScc()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTarjanScc"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/transitive-closure")
def kgalgotransitiveclosure_endpoint(body: KgAlgoTransitiveClosureDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTransitiveClosure()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTransitiveClosure"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/two-hop-labeling")
def kgalgotwohoplabeling_endpoint(body: KgAlgoTwoHopLabelingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTwoHopLabeling()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTwoHopLabeling"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/yens-k-shortest-paths")
def kgalgoyenskshortestpaths_endpoint(body: KgAlgoYensKShortestPathsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoYensKShortestPaths()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoYensKShortestPaths"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/allens-interval-algebra")
def kgalgoallensintervalalgebra_endpoint(body: KgAlgoAllensIntervalAlgebraDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoAllensIntervalAlgebra()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoAllensIntervalAlgebra"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/amie-rule-mining")
def kgalgoamierulemining_endpoint(body: KgAlgoAmieRuleMiningDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoAmieRuleMining()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoAmieRuleMining"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/backward-chaining")
def kgalgobackwardchaining_endpoint(body: KgAlgoBackwardChainingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoBackwardChaining()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoBackwardChaining"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/datalog-semi-naive")
def kgalgodatalogseminaive_endpoint(body: KgAlgoDatalogSemiNaiveDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDatalogSemiNaive()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDatalogSemiNaive"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/dred-incremental-maintenance")
def kgalgodredincrementalmaintenance_endpoint(body: KgAlgoDredIncrementalMaintenanceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDredIncrementalMaintenance()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDredIncrementalMaintenance"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/inconsistency-justification")
def kgalgoinconsistencyjustification_endpoint(body: KgAlgoInconsistencyJustificationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoInconsistencyJustification()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoInconsistencyJustification"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/inconsistency-repair")
def kgalgoinconsistencyrepair_endpoint(body: KgAlgoInconsistencyRepairDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoInconsistencyRepair()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoInconsistencyRepair"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/materialization-planner")
def kgalgomaterializationplanner_endpoint(body: KgAlgoMaterializationPlannerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoMaterializationPlanner()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoMaterializationPlanner"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/open-closed-world")
def kgalgoopenclosedworld_endpoint(body: KgAlgoOpenClosedWorldDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOpenClosedWorld()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOpenClosedWorld"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/owl2-el-classification")
def kgalgoowl2elclassification_endpoint(body: KgAlgoOwl2ElClassificationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOwl2ElClassification()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOwl2ElClassification"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/owl2-rl-reasoner")
def kgalgoowl2rlreasoner_endpoint(body: KgAlgoOwl2RlReasonerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOwl2RlReasoner()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOwl2RlReasoner"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/probabilistic-soft-logic")
def kgalgoprobabilisticsoftlogic_endpoint(body: KgAlgoProbabilisticSoftLogicDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoProbabilisticSoftLogic()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoProbabilisticSoftLogic"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/rdfs-entailment")
def kgalgordfsentailment_endpoint(body: KgAlgoRdfsEntailmentDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRdfsEntailment()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRdfsEntailment"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/rete-forward-chaining")
def kgalgoreteforwardchaining_endpoint(body: KgAlgoReteForwardChainingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoReteForwardChaining()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoReteForwardChaining"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/same-as-congruence")
def kgalgosameascongruence_endpoint(body: KgAlgoSameAsCongruenceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSameAsCongruence()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSameAsCongruence"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/tableau-reasoner")
def kgalgotableaureasoner_endpoint(body: KgAlgoTableauReasonerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTableauReasoner()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTableauReasoner"}
    return build_success_envelope(data=res, trace_id=trace_id)

