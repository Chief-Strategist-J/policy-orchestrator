"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH SYSTEMS ROUTER

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Part 7: Graphs in Systems & Infrastructure (ALGO-GRAPH-SYS-301 through ALGO-GRAPH-SYS-320):
- Scheduling and Build Systems (Register Allocation, CPM/PERT, Coffman-Graham, HEFT, Build Dependency Graphs)
- Memory and Resource Graphs (Tracing GC, Bacon-Rajan Cycle Collection, Chandy-Misra-Haas Deadlock)
- Networks and Protocols (Gossip Protocols, Consensus Averaging, Reliability, OSPF/RIP Routing, BGP Path Vector, STP)
- Layout and Visualization (Force-Directed, Sugiyama Hierarchical, Edge Bundling)
- Geometry, Maps, and Security (Delaunay/Voronoi/EMST, Map Matching HMM, Attack Graph Path Analysis)

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.graph.graphs_in_systems import (
    GraphAlgoChaitinBriggsRegisterAllocation,
    GraphAlgoCriticalPathPert,
    GraphAlgoCoffmanGrahamScheduling,
    GraphAlgoHeftHeterogeneousScheduling,
    GraphAlgoBuildSystemDependencyGraphs,
    GraphAlgoTracingGarbageCollection,
    GraphAlgoBaconRajanCycleCollection,
    GraphAlgoChandyMisraHaasDeadlock,
    GraphAlgoGossipEpidemicProtocols,
    GraphAlgoConsensusAveragingLaplacian,
    GraphAlgoNetworkReliabilityMonteCarlo,
    GraphAlgoLinkStateDistanceVectorRouting,
    GraphAlgoPathVectorBgpRouting,
    GraphAlgoSpanningTreeProtocolStp,
    GraphAlgoForceDirectedLayoutBarnesHut,
    GraphAlgoSugiyamaHierarchicalLayout,
    GraphAlgoEdgeBundlingVisualization,
    GraphAlgoGeometricDelaunayVoronoiEmst,
    GraphAlgoMapMatchingHmmViterbi,
    GraphAlgoAttackGraphPathAnalysis,
)

router = APIRouter(prefix="/algos/graph/systems", tags=["Graph Systems Algorithms"])


class RegisterAllocationDTO(BaseModel):
    interference_adjacency: Dict[str, List[str]] = Field(..., description="Interference graph between variables")
    k_registers: int = Field(..., description="Number of available physical CPU registers")
    spill_costs: Optional[Dict[str, float]] = Field(default=None, description="Optional spill cost per variable")


class CriticalPathPertDTO(BaseModel):
    dependency_dag: Dict[str, List[str]] = Field(..., description="Task dependency DAG (task -> successors)")
    durations: Dict[str, Any] = Field(..., description="Durations (single float or optimistic/most_likely/pessimistic tuple)")


class CoffmanGrahamDTO(BaseModel):
    precedence_dag: Dict[str, List[str]] = Field(..., description="Precedence task graph")
    num_processors: int = Field(default=2, description="Number of parallel execution workers/processors")


class HeftSchedulingDTO(BaseModel):
    precedence_dag: Dict[str, List[str]] = Field(..., description="Precedence DAG of tasks")
    computation_costs: Dict[str, Dict[str, float]] = Field(..., description="Computation cost per task per machine")
    processors: List[str] = Field(..., description="List of available processor IDs")
    communication_costs: Optional[Dict[str, float]] = Field(default=None, description="Edge communication costs")


class BuildSystemDependencyDTO(BaseModel):
    task_dependencies: Dict[str, List[str]] = Field(..., description="Task build dependency graph")
    input_file_hashes: Dict[str, str] = Field(..., description="Current cryptographic hashes of input files")
    task_input_files: Optional[Dict[str, List[str]]] = Field(default=None, description="Input files per task")


class TracingGarbageCollectionDTO(BaseModel):
    references: Dict[str, List[str]] = Field(..., description="Object reference graph")
    roots: List[str] = Field(..., description="Designated active root object pointers")
    generations: Optional[Dict[str, int]] = Field(default=None, description="Optional generation IDs (0=young, 1=old)")


class BaconRajanCycleCollectionDTO(BaseModel):
    references: Dict[str, List[str]] = Field(..., description="Object reference graph")
    external_ref_counts: Dict[str, int] = Field(..., description="Total current incoming reference counts")
    candidate_roots: List[str] = Field(..., description="Decremented candidate root objects")


class ChandyMisraHaasDeadlockDTO(BaseModel):
    wait_for_graph: Dict[str, List[str]] = Field(..., description="Distributed wait-for dependency graph")
    initiators: Optional[List[str]] = Field(default=None, description="Optional list of probe initiator nodes")
    process_priorities: Optional[Dict[str, int]] = Field(default=None, description="Optional process priority weights")


class GossipEpidemicDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Communication overlay topology")
    initial_state: Dict[str, Dict[str, Tuple[Any, int]]] = Field(..., description="Initial node key-value version state")
    mode: str = Field(default="push_pull", description="Dissemination mode ('push', 'pull', 'push_pull')")
    fanout: int = Field(default=2, description="Gossip fanout peer count")
    max_rounds: int = Field(default=30, description="Maximum simulation rounds")


class ConsensusAveragingLaplacianDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Communication graph topology")
    initial_values: Dict[str, float] = Field(..., description="Initial scalar state per node")
    epsilon: float = Field(default=0.1, description="Laplacian consensus step size")
    max_iterations: int = Field(default=100, description="Maximum consensus rounds")
    method: str = Field(default="laplacian", description="Method ('laplacian' or 'push_sum')")


class NetworkReliabilityMonteCarloDTO(BaseModel):
    edges: List[Tuple[str, str, float]] = Field(..., description="Edges with failure probabilities (u, v, q_fail)")
    nodes: List[str] = Field(..., description="List of all vertices in network")
    source: Optional[str] = Field(default=None, description="Optional source node for 2-terminal reliability")
    target: Optional[str] = Field(default=None, description="Optional target node for 2-terminal reliability")
    num_samples: int = Field(default=1000, description="Monte Carlo simulation trials")


class LinkStateDistanceVectorRoutingDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Weighted directed link topology")
    protocol: str = Field(default="link_state", description="Protocol ('link_state' or 'distance_vector')")
    split_horizon: bool = Field(default=True, description="Enable split horizon rule")
    poison_reverse: bool = Field(default=True, description="Enable poison reverse")


class PathVectorBgpRoutingDTO(BaseModel):
    as_topology: Dict[str, List[str]] = Field(..., description="AS-level peering topology")
    relationships: Dict[str, str] = Field(..., description="Peering relationships (e.g. 'AS1:AS2' -> 'customer')")
    prefix_origins: Dict[str, str] = Field(..., description="Prefix origin mappings (prefix -> originating AS)")
    max_rounds: int = Field(default=20, description="Maximum route propagation rounds")


class SpanningTreeProtocolStpDTO(BaseModel):
    bridge_priorities: Dict[str, int] = Field(..., description="Priority values per bridge/switch")
    links: List[Tuple[str, str, float]] = Field(..., description="Network links (bridge_u, bridge_v, cost)")


class ForceDirectedLayoutDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph topology")
    iterations: int = Field(default=50, description="Simulation steps")
    width: float = Field(default=1000.0, description="Bounding box width")
    height: float = Field(default=1000.0, description="Bounding box height")


class SugiyamaHierarchicalLayoutDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Directed graph topology")
    layer_distance: float = Field(default=100.0, description="Vertical layer distance")
    node_distance: float = Field(default=80.0, description="Horizontal node spacing")
    sweeps: int = Field(default=4, description="Crossing reduction sweep iterations")


class EdgeBundlingVisualizationDTO(BaseModel):
    edges: List[Tuple[str, str]] = Field(..., description="Edges to be bundled")
    node_positions: Dict[str, Tuple[float, float]] = Field(..., description="2D node coordinates (x, y)")
    num_segments: int = Field(default=4, description="Subdivision segments per edge")
    iterations: int = Field(default=10, description="Bundling attraction cycles")


class GeometricDelaunayVoronoiEmstDTO(BaseModel):
    points: Dict[str, Tuple[float, float]] = Field(..., description="Spatial 2D point coordinates")


class MapMatchingHmmViterbiDTO(BaseModel):
    road_segments: Dict[str, Tuple[Tuple[float, float], Tuple[float, float]]] = Field(..., description="Road segments mapping id -> (start_pt, end_pt)")
    road_adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Segment-to-segment connectivity graph")
    gps_trace: List[Tuple[float, float]] = Field(..., description="Recorded GPS coordinate sequence")
    sigma_z: float = Field(default=10.0, description="Observation noise std dev")
    beta: float = Field(default=5.0, description="Transition penalty scale")


class AttackGraphPathAnalysisDTO(BaseModel):
    initial_facts: List[str] = Field(..., description="Ground security facts")
    derivation_rules: List[Dict[str, Any]] = Field(..., description="Datalog derivation rule specifications")
    target_assets: List[str] = Field(..., description="Crown jewel asset targets")


@router.post("/register-allocation")
def register_allocation_endpoint(payload: RegisterAllocationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoChaitinBriggsRegisterAllocation[str]().evaluate(
        interference_adjacency=payload.interference_adjacency,
        k_registers=payload.k_registers,
        spill_costs=payload.spill_costs,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/critical-path-pert")
def critical_path_pert_endpoint(payload: CriticalPathPertDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoCriticalPathPert[str]().evaluate(
        dependency_dag=payload.dependency_dag,
        durations=payload.durations,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/coffman-graham-scheduling")
def coffman_graham_scheduling_endpoint(payload: CoffmanGrahamDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoCoffmanGrahamScheduling[str]().evaluate(
        precedence_dag=payload.precedence_dag,
        num_processors=payload.num_processors,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/heft-scheduling")
def heft_scheduling_endpoint(payload: HeftSchedulingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoHeftHeterogeneousScheduling[str]().evaluate(
        precedence_dag=payload.precedence_dag,
        computation_costs=payload.computation_costs,
        processors=payload.processors,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/build-system-dependencies")
def build_system_dependencies_endpoint(payload: BuildSystemDependencyDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoBuildSystemDependencyGraphs[str]().evaluate(
        task_dependencies=payload.task_dependencies,
        input_file_hashes=payload.input_file_hashes,
        task_input_files=payload.task_input_files,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/tracing-garbage-collection")
def tracing_garbage_collection_endpoint(payload: TracingGarbageCollectionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoTracingGarbageCollection[str]().evaluate(
        references=payload.references,
        roots=set(payload.roots),
        generations=payload.generations,
    )
    return build_success_envelope(
        data={
            "live_objects": list(res["live_objects"]),
            "garbage_objects": list(res["garbage_objects"]),
            "tri_color_states": res["tri_color_states"],
            "generational_summary": res["generational_summary"],
            "barrier_shades": res["barrier_shades"],
        },
        trace_id=trace_id,
    )


@router.post("/bacon-rajan-cycle-collection")
def bacon_rajan_cycle_collection_endpoint(payload: BaconRajanCycleCollectionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoBaconRajanCycleCollection[str]().evaluate(
        references=payload.references,
        external_ref_counts=payload.external_ref_counts,
        candidate_roots=payload.candidate_roots,
    )
    return build_success_envelope(
        data={
            "collected_cycles": [list(c) for c in res["collected_cycles"]],
            "freed_nodes": list(res["freed_nodes"]),
            "surviving_nodes": list(res["surviving_nodes"]),
            "final_ref_counts": res["final_ref_counts"],
        },
        trace_id=trace_id,
    )


@router.post("/chandy-misra-haas-deadlock")
def chandy_misra_haas_deadlock_endpoint(payload: ChandyMisraHaasDeadlockDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoChandyMisraHaasDeadlock[str]().evaluate(
        wait_for_graph=payload.wait_for_graph,
        initiators=payload.initiators,
        process_priorities=payload.process_priorities,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/gossip-epidemic-protocols")
def gossip_epidemic_protocols_endpoint(payload: GossipEpidemicDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoGossipEpidemicProtocols[str]().evaluate(
        adjacency=payload.adjacency,
        initial_state=payload.initial_state,
        mode=payload.mode,
        fanout=payload.fanout,
        max_rounds=payload.max_rounds,
    )
    return build_success_envelope(
        data={
            "rounds_to_convergence": res["rounds_to_convergence"],
            "converged": res["converged"],
            "final_states": res["final_states"],
            "message_count": res["message_count"],
            "suspected_failed_nodes": list(res["suspected_failed_nodes"]),
        },
        trace_id=trace_id,
    )


@router.post("/consensus-averaging-laplacian")
def consensus_averaging_laplacian_endpoint(payload: ConsensusAveragingLaplacianDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoConsensusAveragingLaplacian[str]().evaluate(
        adjacency=payload.adjacency,
        initial_values=payload.initial_values,
        epsilon=payload.epsilon,
        max_iterations=payload.max_iterations,
        method=payload.method,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/network-reliability-monte-carlo")
def network_reliability_monte_carlo_endpoint(payload: NetworkReliabilityMonteCarloDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoNetworkReliabilityMonteCarlo[str]().evaluate(
        edges=payload.edges,
        nodes=payload.nodes,
        source=payload.source,
        target=payload.target,
        num_samples=payload.num_samples,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/link-state-distance-vector-routing")
def link_state_distance_vector_routing_endpoint(payload: LinkStateDistanceVectorRoutingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoLinkStateDistanceVectorRouting[str]().evaluate(
        adjacency=payload.adjacency,
        protocol=payload.protocol,
        split_horizon=payload.split_horizon,
        poison_reverse=payload.poison_reverse,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/path-vector-bgp-routing")
def path_vector_bgp_routing_endpoint(payload: PathVectorBgpRoutingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    parsed_rels = {}
    for k, v in payload.relationships.items():
        parts = k.split(":")
        if len(parts) == 2:
            parsed_rels[(parts[0], parts[1])] = v
    res = GraphAlgoPathVectorBgpRouting[str]().evaluate(
        as_topology=payload.as_topology,
        relationships=parsed_rels,
        prefix_origins=payload.prefix_origins,
        max_rounds=payload.max_rounds,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/spanning-tree-protocol-stp")
def spanning_tree_protocol_stp_endpoint(payload: SpanningTreeProtocolStpDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoSpanningTreeProtocolStp[str]().evaluate(
        bridge_priorities=payload.bridge_priorities,
        links=payload.links,
    )
    roles_serializable = {f"{u}:{v}": role for (u, v), role in res["port_roles"].items()}
    return build_success_envelope(
        data={
            "root_bridge": res["root_bridge"],
            "root_path_costs": res["root_path_costs"],
            "port_roles": roles_serializable,
            "active_spanning_tree_edges": res["active_spanning_tree_edges"],
            "blocked_edges": res["blocked_edges"],
        },
        trace_id=trace_id,
    )


@router.post("/force-directed-layout")
def force_directed_layout_endpoint(payload: ForceDirectedLayoutDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoForceDirectedLayoutBarnesHut[str]().evaluate(
        adjacency=payload.adjacency,
        iterations=payload.iterations,
        width=payload.width,
        height=payload.height,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/sugiyama-hierarchical-layout")
def sugiyama_hierarchical_layout_endpoint(payload: SugiyamaHierarchicalLayoutDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoSugiyamaHierarchicalLayout[str]().evaluate(
        adjacency=payload.adjacency,
        layer_distance=payload.layer_distance,
        node_distance=payload.node_distance,
        sweeps=payload.sweeps,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/edge-bundling-visualization")
def edge_bundling_visualization_endpoint(payload: EdgeBundlingVisualizationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoEdgeBundlingVisualization[str]().evaluate(
        edges=payload.edges,
        node_positions=payload.node_positions,
        num_segments=payload.num_segments,
        iterations=payload.iterations,
    )
    paths_serializable = {f"{u}:{v}": pts for (u, v), pts in res["bundled_paths"].items()}
    compat_serializable = {f"{i}:{j}": score for (i, j), score in res["compatibility_matrix"].items()}
    return build_success_envelope(
        data={
            "bundled_paths": paths_serializable,
            "compatibility_matrix": compat_serializable,
            "bundle_clusters": res["bundle_clusters"],
            "mean_curvature": res["mean_curvature"],
        },
        trace_id=trace_id,
    )


@router.post("/geometric-delaunay-voronoi-emst")
def geometric_delaunay_voronoi_emst_endpoint(payload: GeometricDelaunayVoronoiEmstDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoGeometricDelaunayVoronoiEmst[str]().evaluate(points=payload.points)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/map-matching-hmm-viterbi")
def map_matching_hmm_viterbi_endpoint(payload: MapMatchingHmmViterbiDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoMapMatchingHmmViterbi[str]().evaluate(
        road_segments=payload.road_segments,
        road_adjacency=payload.road_adjacency,
        gps_trace=payload.gps_trace,
        sigma_z=payload.sigma_z,
        beta=payload.beta,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/attack-graph-path-analysis")
def attack_graph_path_analysis_endpoint(payload: AttackGraphPathAnalysisDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = GraphAlgoAttackGraphPathAnalysis[str]().evaluate(
        initial_facts=payload.initial_facts,
        derivation_rules=payload.derivation_rules,
        target_assets=payload.target_assets,
    )
    return build_success_envelope(data=res, trace_id=trace_id)
