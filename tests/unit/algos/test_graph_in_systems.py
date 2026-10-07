"""
Unit tests for Graph Algorithms in Systems & Infrastructure (ALGO-GRAPH-SYS-301 through ALGO-GRAPH-SYS-320).
"""

import pytest
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


def test_301_chaitin_briggs_register_allocation():
    algo = GraphAlgoChaitinBriggsRegisterAllocation[str]()
    interference = {
        "v1": ["v2", "v3"],
        "v2": ["v1", "v3"],
        "v3": ["v1", "v2"],
        "v4": ["v3"],
    }
    res = algo.evaluate(interference_adjacency=interference, k_registers=3)
    assert res["is_successful"] is True
    assert len(res["register_allocation"]) == 4
    assert res["register_allocation"]["v1"] != res["register_allocation"]["v2"]
    assert res["register_allocation"]["v1"] != res["register_allocation"]["v3"]
    assert res["register_allocation"]["v2"] != res["register_allocation"]["v3"]


def test_302_critical_path_pert():
    algo = GraphAlgoCriticalPathPert[str]()
    durations = {"A": 3.0, "B": 2.0, "C": 4.0, "D": 2.0}
    dependencies = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    res = algo.evaluate(dependency_dag=dependencies, durations=durations)
    assert res["critical_path"] == ["A", "C", "D"]
    assert res["project_duration"] == 9.0
    assert res["schedule_table"]["C"]["slack"] == 0.0
    assert res["schedule_table"]["B"]["slack"] == 2.0


def test_303_coffman_graham_scheduling():
    algo = GraphAlgoCoffmanGrahamScheduling[str]()
    dependencies = {"T1": ["T2", "T3"], "T2": ["T4"], "T3": ["T4"], "T4": []}
    res = algo.evaluate(precedence_dag=dependencies, num_processors=2)
    assert len(res["schedule"]) > 0
    assert res["makespan"] >= 3
    assert len(res["labels"]) == 4


def test_304_heft_heterogeneous_scheduling():
    algo = GraphAlgoHeftHeterogeneousScheduling[str]()
    computation_costs = {
        "T1": {"m1": 2.0, "m2": 3.0},
        "T2": {"m1": 4.0, "m2": 2.0},
        "T3": {"m1": 3.0, "m2": 3.0},
    }
    dependencies = {"T1": ["T2", "T3"], "T2": [], "T3": []}
    res = algo.evaluate(
        precedence_dag=dependencies,
        computation_costs=computation_costs,
        processors=["m1", "m2"],
    )
    assert len(res["schedule"]) == 3
    assert res["makespan"] > 0.0


def test_305_build_system_dependency_graphs():
    algo = GraphAlgoBuildSystemDependencyGraphs[str]()
    dependencies = {"main.o": ["main.c", "util.h"], "app": ["main.o"]}
    input_hashes = {"main.c": "hash_v1", "util.h": "hash_v1"}
    input_files = {"main.o": ["main.c", "util.h"]}
    res = algo.evaluate(
        task_dependencies=dependencies,
        input_file_hashes=input_hashes,
        task_input_files=input_files,
    )
    assert "main.o" in res["rebuilt_tasks"]
    assert "app" in res["rebuilt_tasks"]


def test_306_tracing_garbage_collection():
    algo = GraphAlgoTracingGarbageCollection[str]()
    references = {
        "root_obj": ["child_1"],
        "child_1": ["grandchild_1"],
        "orphan_1": ["orphan_2"],
        "orphan_2": ["orphan_1"],
    }
    res = algo.evaluate(references=references, roots={"root_obj"})
    assert "root_obj" in res["live_objects"]
    assert "child_1" in res["live_objects"]
    assert "grandchild_1" in res["live_objects"]
    assert "orphan_1" in res["garbage_objects"]
    assert "orphan_2" in res["garbage_objects"]


def test_307_bacon_rajan_cycle_collection():
    algo = GraphAlgoBaconRajanCycleCollection[str]()
    references = {"A": ["B"], "B": ["A"]}
    external_rc = {"A": 1, "B": 1}
    res = algo.evaluate(
        references=references,
        external_ref_counts=external_rc,
        candidate_roots=["A"],
    )
    assert "A" in res["freed_nodes"]
    assert "B" in res["freed_nodes"]


def test_308_chandy_misra_haas_deadlock():
    algo = GraphAlgoChandyMisraHaasDeadlock[str]()
    wfg = {"P1": ["P2"], "P2": ["P3"], "P3": ["P1"]}
    res = algo.evaluate(wait_for_graph=wfg)
    assert res["is_deadlocked"] is True
    assert len(res["deadlocks_detected"]) >= 1
    assert len(res["selected_victims"]) >= 1


def test_309_gossip_epidemic_protocols():
    algo = GraphAlgoGossipEpidemicProtocols[str]()
    adjacency = {"N1": ["N2"], "N2": ["N1", "N3"], "N3": ["N2"]}
    initial_state = {
        "N1": {"config_a": ("v100", 1)},
        "N2": {},
        "N3": {},
    }
    res = algo.evaluate(adjacency=adjacency, initial_state=initial_state, max_rounds=10)
    assert res["converged"] is True
    assert res["final_states"]["N3"].get("config_a") == ("v100", 1)


def test_310_consensus_averaging_laplacian():
    algo = GraphAlgoConsensusAveragingLaplacian[str]()
    adjacency = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    initial_values = {"A": 10.0, "B": 20.0, "C": 30.0}
    res = algo.evaluate(adjacency=adjacency, initial_values=initial_values, epsilon=0.2, max_iterations=200)
    assert res["converged"] is True
    assert pytest.approx(res["consensus_value"], rel=1e-2) == 20.0
    assert pytest.approx(res["target_average"], rel=1e-5) == 20.0


def test_311_network_reliability_monte_carlo():
    algo = GraphAlgoNetworkReliabilityMonteCarlo[str]()
    edges = [("A", "B", 0.05), ("B", "C", 0.05), ("A", "C", 0.1)]
    nodes = ["A", "B", "C"]
    res = algo.evaluate(edges=edges, nodes=nodes, source="A", target="C", num_samples=500)
    assert res["two_terminal_reliability"] is not None
    assert res["two_terminal_reliability"] > 0.8
    assert res["all_terminal_reliability"] > 0.8


def test_312_link_state_distance_vector_routing():
    algo = GraphAlgoLinkStateDistanceVectorRouting[str]()
    adj = {
        "R1": [("R2", 1.0), ("R3", 5.0)],
        "R2": [("R1", 1.0), ("R3", 2.0)],
        "R3": [("R1", 5.0), ("R2", 2.0)],
    }
    res_ls = algo.evaluate(adjacency=adj, protocol="link_state")
    assert res_ls["forwarding_tables"]["R1"]["R3"][0] == "R2"
    assert res_ls["forwarding_tables"]["R1"]["R3"][1] == 3.0

    res_dv = algo.evaluate(adjacency=adj, protocol="distance_vector")
    assert res_dv["forwarding_tables"]["R1"]["R3"][0] == "R2"
    assert res_dv["forwarding_tables"]["R1"]["R3"][1] == 3.0


def test_313_path_vector_bgp_routing():
    algo = GraphAlgoPathVectorBgpRouting[str]()
    topology = {"AS1": ["AS2"], "AS2": ["AS1", "AS3"], "AS3": ["AS2"]}
    relationships = {
        ("AS1", "AS2"): "customer",
        ("AS2", "AS1"): "provider",
        ("AS2", "AS3"): "customer",
        ("AS3", "AS2"): "provider",
    }
    origins = {"192.168.1.0/24": "AS1"}
    res = algo.evaluate(as_topology=topology, relationships=relationships, prefix_origins=origins)
    assert "192.168.1.0/24" in res["loc_rib"]["AS3"]
    assert res["loc_rib"]["AS3"]["192.168.1.0/24"] == ["AS3", "AS2", "AS1"]


def test_314_spanning_tree_protocol_stp():
    algo = GraphAlgoSpanningTreeProtocolStp[str]()
    priorities = {"SW1": 4096, "SW2": 8192, "SW3": 8192}
    links = [("SW1", "SW2", 4.0), ("SW1", "SW3", 4.0), ("SW2", "SW3", 4.0)]
    res = algo.evaluate(bridge_priorities=priorities, links=links)
    assert res["root_bridge"] == "SW1"
    assert len(res["active_spanning_tree_edges"]) == 2
    assert len(res["blocked_edges"]) == 1


def test_315_force_directed_layout_barnes_hut():
    algo = GraphAlgoForceDirectedLayoutBarnesHut[str]()
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
    res = algo.evaluate(adjacency=adj, iterations=20, width=500.0, height=500.0)
    assert len(res["positions"]) == 3
    assert all(0.0 <= p[0] <= 500.0 and 0.0 <= p[1] <= 500.0 for p in res["positions"].values())


def test_316_sugiyama_hierarchical_layout():
    algo = GraphAlgoSugiyamaHierarchicalLayout[str]()
    adj = {"N1": ["N2", "N3"], "N2": ["N4"], "N3": ["N4"], "N4": []}
    res = algo.evaluate(adjacency=adj)
    assert res["layer_assignment"]["N1"] < res["layer_assignment"]["N2"]
    assert res["layer_assignment"]["N2"] < res["layer_assignment"]["N4"]
    assert len(res["node_positions"]) == 4


def test_317_edge_bundling_visualization():
    algo = GraphAlgoEdgeBundlingVisualization[str]()
    edges = [("A", "B"), ("C", "D")]
    positions = {"A": (0.0, 0.0), "B": (100.0, 0.0), "C": (0.0, 10.0), "D": (100.0, 10.0)}
    res = algo.evaluate(edges=edges, node_positions=positions, num_segments=4, iterations=5)
    assert len(res["bundled_paths"]) == 2
    assert len(res["bundle_clusters"]) >= 1


def test_318_geometric_delaunay_voronoi_emst():
    algo = GraphAlgoGeometricDelaunayVoronoiEmst[str]()
    points = {
        "P1": (0.0, 0.0),
        "P2": (10.0, 0.0),
        "P3": (0.0, 10.0),
        "P4": (10.0, 10.0),
    }
    res = algo.evaluate(points=points)
    assert len(res["delaunay_edges"]) >= 5
    assert len(res["emst_edges"]) == 3
    assert res["total_emst_length"] > 0.0


def test_319_map_matching_hmm_viterbi():
    algo = GraphAlgoMapMatchingHmmViterbi[str]()
    segments = {
        "seg_1": ((0.0, 0.0), (100.0, 0.0)),
        "seg_2": ((100.0, 0.0), (200.0, 0.0)),
    }
    adj = {"seg_1": [("seg_2", 100.0)], "seg_2": []}
    trace = [(10.0, 1.0), (50.0, -1.0), (120.0, 0.5)]
    res = algo.evaluate(road_segments=segments, road_adjacency=adj, gps_trace=trace)
    assert len(res["matched_segment_sequence"]) == 3
    assert res["matched_segment_sequence"][0] == "seg_1"
    assert res["matched_segment_sequence"][2] == "seg_2"


def test_320_attack_graph_path_analysis():
    algo = GraphAlgoAttackGraphPathAnalysis[str]()
    facts = ["attacker_on_internet", "vuln_cve_2023_ssh", "network_route_to_host"]
    rules = [
        {
            "name": "rce_ssh",
            "premises": ["attacker_on_internet", "vuln_cve_2023_ssh", "network_route_to_host"],
            "conclusion": "root_on_host",
            "difficulty": 2.0,
        },
        {
            "name": "steal_db_creds",
            "premises": ["root_on_host"],
            "conclusion": "crown_jewel_db_access",
            "difficulty": 1.0,
        },
    ]
    targets = ["crown_jewel_db_access"]
    res = algo.evaluate(initial_facts=facts, derivation_rules=rules, target_assets=targets)
    assert "crown_jewel_db_access" in res["reachable_targets"]
    assert len(res["shortest_attack_paths"]["crown_jewel_db_access"]) >= 3
    assert len(res["minimum_cut_remediations"]) >= 1
