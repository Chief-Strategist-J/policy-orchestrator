"""
================================================================================
COMPREHENSIVE UNIT TESTS: KNOWLEDGE GRAPH MASTER SUITE (PARTS 1 & 2, #1–100)
Role Categorized Architecture:
- Modeling (#1-12, #41-50)
- Storage (#13-24)
- Construction (#25-34)
- Resolution (#35-40)
- Query (#51-62)
- Analytics (#63-84)
- Reasoning (#85-100)
================================================================================
"""

import pytest
from src.features.code_engine.algos.knowledge_graph import (
    # Modeling
    KgAlgoRdfTriples,
    KgAlgoRdfsSchema,
    KgAlgoOwl2Ontology,
    KgAlgoLabeledPropertyGraph,
    KgAlgoShaclShapes,
    KgAlgoSkosConcept,
    KgAlgoJsonLdProcessor,
    KgAlgoIriNamespaces,
    KgAlgoRdfStarReification,
    KgAlgoNamedGraphsQuads,
    KgAlgoSchemaOrgMapper,
    KgAlgoBitemporalModeling,
    KgAlgoOntologyAlignment,
    KgAlgoR2rmlSchemaMapping,
    KgAlgoTaxonomyHearstInduction,
    KgAlgoEntityTypeInference,
    KgAlgoLlmOntologySynthesis,
    KgAlgoSchemaEvolution,
    KgAlgoPropertyGraphConstraints,
    KgAlgoDataQualityEvaluator,
    KgAlgoRelationNormalization,
    KgAlgoTruthDiscoveryConfidence,
    # Storage
    KgAlgoAdjacencyList,
    KgAlgoCsrRepresentation,
    KgAlgoIndexFreeAdjacency,
    KgPointerNode,
    KgPointerEdge,
    KgAlgoHexastorePermutation,
    KgAlgoDictionaryEncoding,
    KgAlgoBtreeLsmStorage,
    KgAlgoCompressedHdt,
    KgAlgoGraphPartitioning,
    KgAlgoHashPartitioning,
    KgAlgoPropertyFulltextIndex,
    KgAlgoHybridGraphVector,
    KgAlgoGraphSnapshotsMvcc,
    # Construction
    KgAlgoTextSegmentation,
    KgAlgoNamedEntityRecognition,
    KgAlgoEntityLinking,
    KgAlgoCoreferenceResolution,
    KgAlgoSupervisedRelationExtraction,
    KgAlgoOpenInformationExtraction,
    KgAlgoLlmSchemaExtraction,
    KgAlgoEventExtraction,
    KgAlgoAttributeNormalization,
    KgAlgoStructuredTableExtraction,
    # Resolution
    KgAlgoEntityResolutionBlocking,
    KgAlgoFellegiSunterLinkage,
    KgAlgoSimilarityJoins,
    KgAlgoMatchClustering,
    KgAlgoEntityCanonicalization,
    KgAlgoRelationCanonicalization,
    # Query
    KgAlgoSparqlEngine,
    KgAlgoOpencypherMatcher,
    KgAlgoGqlEvaluator,
    KgAlgoGremlinTraversal,
    KgAlgoVf2SubgraphIsomorphism,
    KgAlgoLeapfrogTriejoin,
    KgAlgoJoinOrderingCardinality,
    KgAlgoRegularPathQueries,
    KgAlgoFederatedQueries,
    KgAlgoObdaQueryRewriting,
    KgAlgoParameterizedTemplates,
    KgAlgoPaginationCaching,
    # Analytics
    KgAlgoBfsTraversal,
    KgAlgoDfsTraversal,
    KgAlgoBidirectionalBfs,
    KgAlgoDijkstraShortestPath,
    KgAlgoAstarSearch,
    KgAlgoYensKShortestPaths,
    KgAlgoRandomWalkRestart,
    KgAlgoMetapathTraversal,
    KgAlgoTwoHopLabeling,
    KgAlgoTransitiveClosure,
    KgAlgoDegreeCentrality,
    KgAlgoPagerankCentrality,
    KgAlgoPersonalizedPagerank,
    KgAlgoBrandesBetweenness,
    KgAlgoClosenessHarmonic,
    KgAlgoHitsCentrality,
    KgAlgoConnectedComponents,
    KgAlgoTarjanScc,
    KgAlgoLouvainCommunity,
    KgAlgoLeidenCommunity,
    KgAlgoLabelPropagation,
    KgAlgoKCoreDecomposition,
    # Reasoning
    KgAlgoRdfsEntailment,
    KgAlgoOwl2RlReasoner,
    KgAlgoReteForwardChaining,
    KgAlgoBackwardChaining,
    KgAlgoDatalogSemiNaive,
    KgAlgoMaterializationPlanner,
    KgAlgoDredIncrementalMaintenance,
    KgAlgoSameAsCongruence,
    KgAlgoTableauReasoner,
    KgAlgoOwl2ElClassification,
    KgAlgoAmieRuleMining,
    KgAlgoOpenClosedWorld,
    KgAlgoInconsistencyJustification,
    KgAlgoProbabilisticSoftLogic,
    KgAlgoAllensIntervalAlgebra,
    KgAlgoInconsistencyRepair,
)

# ==================== 1. MODELING TESTS ====================

def test_rdf_triples():
    algo = KgAlgoRdfTriples()
    nt = "<http://example.org/Alice> <http://xmlns.com/foaf/0.1/knows> <http://example.org/Bob> .\n"
    res = algo.parse_ntriples(nt)
    assert res["triple_count"] == 1

def test_rdfs_schema():
    algo = KgAlgoRdfsSchema()
    sub_classes = [{"child": "Dog", "parent": "Mammal"}, {"child": "Mammal", "parent": "Animal"}]
    instances = [{"entity": "Fido", "class": "Dog"}]
    res = algo.infer_hierarchy(sub_classes, instances)
    assert len(res["inferred_types"]) == 3

def test_owl2_ontology():
    algo = KgAlgoOwl2Ontology()
    facts = [{"subject": "urn:person1", "predicate": "type", "object": "Male"}, {"subject": "urn:person1", "predicate": "type", "object": "Female"}]
    res = algo.check_axioms(facts, disjoint_pairs=[("Male", "Female")], functional_props=[])
    assert res["valid"] is False

def test_labeled_property_graph():
    lpg = KgAlgoLabeledPropertyGraph()
    lpg.add_node("n1", ["User"], {"name": "Alice"})
    lpg.add_node("n2", ["Organization"], {"name": "TechCorp"})
    lpg.add_edge("n1", "n2", "MEMBER_OF", {"role": "Engineer"})
    assert lpg.to_graph_data()["node_count"] == 2

def test_shacl_shapes():
    algo = KgAlgoShaclShapes()
    nodes = [{"id": "n1", "labels": ["User"], "properties": {"name": "Alice", "age": 30}}]
    shapes = [{"target_class": "User", "property_shapes": [{"path": "name", "min_count": 1, "datatype": "string"}]}]
    assert algo.validate_shapes(nodes, shapes)["conforms"] is True

def test_skos_concept():
    algo = KgAlgoSkosConcept()
    res = algo.build_taxonomy([{"subject": "ML", "predicate": "skos:broader", "object": "AI"}])
    assert "AI" in res["top_concepts"]

def test_jsonld_processor():
    algo = KgAlgoJsonLdProcessor()
    doc = {"@context": {"name": "schema:name"}, "name": "Alice"}
    assert algo.expand_document(doc)["expanded_nodes"][0]["schema:name"] == "Alice"

def test_iri_namespaces():
    algo = KgAlgoIriNamespaces()
    assert algo.expand_curie("schema:Person") == "https://schema.org/Person"
    assert algo.compact_iri("https://schema.org/Person") == "schema:Person"

def test_rdf_star_reification():
    algo = KgAlgoRdfStarReification()
    res = algo.reify_triple("Alice", "knows", "Bob", {"confidence": 0.95})
    assert res["quoted_triple"] == "<< Alice knows Bob >>"

def test_named_graphs_quads():
    algo = KgAlgoNamedGraphsQuads()
    algo.add_quad("Alice", "knows", "Bob", "urn:graph:social")
    assert algo.get_dataset_stats()["total_quads"] == 1

def test_schema_org_mapper():
    algo = KgAlgoSchemaOrgMapper()
    res = algo.map_entity_to_schema_org({"type": "user", "name": "Alice"})
    assert res["schema_type"] == "schema:Person"

def test_bitemporal_modeling():
    algo = KgAlgoBitemporalModeling()
    facts = [{"fact": "Alice is CEO", "valid_from": 100.0, "valid_to": 200.0, "tx_from": 50.0, "tx_to": float("inf")}]
    assert algo.query_as_of(facts, valid_at=150.0, system_at=100.0)["active_facts_count"] == 1

def test_ontology_alignment():
    algo = KgAlgoOntologyAlignment()
    res = algo.align_concepts(["ont1:Person"], ["ont2:Person"])
    assert res[0]["similarity"] == 1.0

def test_r2rml_schema_mapping():
    algo = KgAlgoR2rmlSchemaMapping()
    data = [{"emp_id": 101, "name": "Alice"}]
    spec = {"subject_template": "urn:emp:{emp_id}", "predicate_object_maps": [{"predicate": "schema:name", "column": "name"}]}
    assert algo.apply_mapping(data, spec)["count"] == 1

def test_taxonomy_hearst_induction():
    algo = KgAlgoTaxonomyHearstInduction()
    res = algo.extract_hypernyms("Languages such as Python, Rust are popular.")
    assert len(res) >= 1

def test_entity_type_inference():
    algo = KgAlgoEntityTypeInference()
    triples = [{"subject": "Alice", "predicate": "writesCodeFor", "object": "TechCorp"}]
    schema = {"writesCodeFor": {"domain": "Developer", "range": "Company"}}
    res = algo.infer_types(triples, schema)
    assert len(res["inferences"]) == 2

def test_llm_ontology_synthesis():
    algo = KgAlgoLlmOntologySynthesis()
    res = algo.synthesize_ontology("FinTech", ["Account", "Tx"], ["transfersTo"])
    assert len(res["classes"]) == 2

def test_schema_evolution():
    algo = KgAlgoSchemaEvolution()
    v1 = {"classes": ["User", "Admin"]}; v2 = {"classes": ["User", "Admin", "SuperAdmin"]}
    assert algo.check_compatibility(v1, v2)["backward_compatible"] is True

def test_property_graph_constraints():
    algo = KgAlgoPropertyGraphConstraints()
    nodes = [{"id": "n1", "properties": {"email": "a@test.com"}}, {"id": "n2", "properties": {"email": "a@test.com"}}]
    assert algo.enforce_constraints(nodes, unique_properties=["email"], required_properties=["email"])["valid"] is False

def test_data_quality_evaluator():
    algo = KgAlgoDataQualityEvaluator()
    nodes = [{"id": "n1", "labels": ["User"]}, {"id": "n2", "labels": ["Org"]}]
    edges = [{"source": "n1", "target": "n2"}]
    assert algo.evaluate_quality(nodes, edges)["quality_grade"] == "HIGH"

def test_relation_normalization():
    algo = KgAlgoRelationNormalization()
    triples = [{"subject": "Bob", "predicate": "siblingOf", "object": "Alice"}]
    assert algo.normalize_graph(triples)["triples"][0]["subject"] == "Alice"

def test_truth_discovery_confidence():
    algo = KgAlgoTruthDiscoveryConfidence()
    claims = [{"subject": "Earth", "predicate": "shape", "object": "Sphere", "source": "NASA"}]
    assert algo.compute_fact_confidence(claims, {"NASA": 0.99})["fact_count"] == 1

# ==================== 2. STORAGE TESTS ====================

def test_adjacency_list():
    algo = KgAlgoAdjacencyList()
    algo.add_edge("A", "B", "friend")
    assert len(algo.get_neighbors("A", "out")) == 1

def test_csr_representation():
    algo = KgAlgoCsrRepresentation()
    res = algo.build_csr(3, [(0, 1), (0, 2), (1, 2)])
    assert res["num_edges"] == 3

def test_index_free_adjacency():
    algo = KgAlgoIndexFreeAdjacency()
    n1 = KgPointerNode("A"); n2 = KgPointerNode("B")
    n1.first_outgoing = KgPointerEdge(n1, n2, "points_to")
    assert algo.traverse_outgoing(n1)[0]["target"] == "B"

def test_hexastore_permutation():
    algo = KgAlgoHexastorePermutation()
    algo.insert_triple("Alice", "knows", "Bob")
    assert len(algo.query(s="Alice", p="knows")) == 1

def test_dictionary_encoding():
    algo = KgAlgoDictionaryEncoding()
    triples = [("Alice", "knows", "Bob")]
    encoded = algo.encode_triples(triples)
    assert algo.decode(encoded[0][0]) == "Alice"

def test_btree_lsm_storage():
    algo = KgAlgoBtreeLsmStorage(max_memtable_size=2)
    algo.put_fact("fact1", "val1")
    assert algo.get_fact("fact1") == "val1"

def test_compressed_hdt():
    algo = KgAlgoCompressedHdt()
    res = algo.encode_hdt([("Alice", "knows", "Bob")], {"source": "test"})
    assert res["total_triples"] == 1

def test_graph_partitioning():
    algo = KgAlgoGraphPartitioning()
    res = algo.partition_edge_cut(["A", "B", "C", "D"], [("A", "B"), ("C", "D")], num_partitions=2)
    assert res["num_partitions"] == 2

def test_hash_partitioning():
    algo = KgAlgoHashPartitioning()
    res = algo.assign_nodes_and_edges(["A", "B"], [("A", "B")], num_shards=2)
    assert "A" in res["node_assignments"]

def test_property_fulltext_index():
    algo = KgAlgoPropertyFulltextIndex()
    algo.index_node("node_1", {"title": "Fast Neural Knowledge Graphs"})
    assert algo.search("Neural Knowledge") == ["node_1"]

def test_hybrid_graph_vector():
    algo = KgAlgoHybridGraphVector()
    algo.add_vector("n1", [1.0, 0.0])
    hits = algo.search_similar_nodes([1.0, 0.0], top_k=1)
    assert hits[0]["node_id"] == "n1"

def test_graph_snapshots_mvcc():
    algo = KgAlgoGraphSnapshotsMvcc()
    snap = algo.commit_snapshot({"entity_1": "v1"}, author="eng")
    assert algo.get_snapshot(snap["snapshot_id"])["entity_1"] == "v1"

# ==================== 3. CONSTRUCTION TESTS ====================

def test_text_segmentation():
    algo = KgAlgoTextSegmentation()
    assert algo.segment_text("First sentence. Second sentence!")["sentence_count"] == 2

def test_named_entity_recognition():
    algo = KgAlgoNamedEntityRecognition()
    assert algo.extract_entities("Dr. Alan Turing founded Turing Corp in London.")["entity_count"] >= 1

def test_entity_linking():
    algo = KgAlgoEntityLinking()
    kb = {"kb_apple": {"name": "Apple", "aliases": ["Apple Inc."]}}
    assert algo.link_entities([{"text": "Apple Inc."}], kb)["linked_results"][0]["kb_id"] == "kb_apple"

def test_coreference_resolution():
    algo = KgAlgoCoreferenceResolution()
    res = algo.resolve_pronouns(["Alice visited London.", "She liked the museum."])
    assert "[Alice]" in res["resolved_sentences"][1]

def test_supervised_relation_extraction():
    algo = KgAlgoSupervisedRelationExtraction()
    assert len(algo.extract_relations("Alice founded TechCorp today.")["relations"]) == 1

def test_open_information_extraction():
    algo = KgAlgoOpenInformationExtraction()
    assert algo.extract_open_triples("Alice loves Python")["triple_count"] >= 1

def test_llm_schema_extraction():
    algo = KgAlgoLlmSchemaExtraction()
    raw = {"entities": [{"text": "Alice", "type": "Person"}], "relations": []}
    assert len(algo.extract_with_schema(raw, ["Person"], [])["extracted_entities"]) == 1

def test_event_extraction():
    algo = KgAlgoEventExtraction()
    assert algo.extract_event("Acquisition", "BusinessEvent", [], "2026-01-01", "NYC")["event_type"] == "BusinessEvent"

def test_attribute_normalization():
    algo = KgAlgoAttributeNormalization()
    assert algo.normalize_value("250 MB")["normalized_value"] == 250.0

def test_structured_table_extraction():
    algo = KgAlgoStructuredTableExtraction()
    assert algo.table_to_triples([{"id": 1, "name": "Alice"}], "id", "User")["triple_count"] == 2

# ==================== 4. RESOLUTION TESTS ====================

def test_entity_resolution_blocking():
    algo = KgAlgoEntityResolutionBlocking()
    records = [{"id": 1, "name": "Robert"}, {"id": 2, "name": "Rob"}]
    assert len(algo.generate_blocks(records, "name")["rob"]) == 2

def test_fellegi_sunter_linkage():
    algo = KgAlgoFellegiSunterLinkage()
    rec_a = {"name": "Alice", "zip": "90210"}; rec_b = {"name": "Alice", "zip": "90210"}
    assert algo.evaluate_pair(rec_a, rec_b, ["name", "zip"], threshold=1.0)["is_match"] is True

def test_similarity_joins():
    algo = KgAlgoSimilarityJoins()
    list_a = [{"id": 1, "title": "deep learning for graphs"}]; list_b = [{"id": 2, "title": "deep learning for knowledge graphs"}]
    assert len(algo.join_pairs(list_a, list_b, "title", min_similarity=0.6)) == 1

def test_match_clustering():
    algo = KgAlgoMatchClustering()
    assert algo.cluster_pairs([("A", "B"), ("B", "C")])["cluster_count"] == 1

def test_entity_canonicalization():
    algo = KgAlgoEntityCanonicalization()
    records = [{"name": "Robert Smith", "city": "NYC"}, {"name": "Rob Smith", "city": "NYC"}]
    assert algo.synthesize_golden_record(records)["golden_record"]["city"] == "NYC"

def test_relation_canonicalization():
    algo = KgAlgoRelationCanonicalization()
    triples = [{"subject": "Alice", "predicate": "bought", "object": "Book"}]
    assert algo.canonicalize_triples(triples)["canonical_triples"][0]["predicate"] == "acquired"

# ==================== 5. QUERY TESTS ====================

def test_sparql_engine():
    algo = KgAlgoSparqlEngine()
    triples = [{"subject": "Alice", "predicate": "knows", "object": "Bob"}]
    bgp = [("?person", "knows", "Bob")]
    assert algo.execute_bgp(triples, bgp)["bindings"][0]["?person"] == "Alice"

def test_opencypher_matcher():
    algo = KgAlgoOpencypherMatcher()
    nodes = [{"id": "n1", "name": "Alice"}, {"id": "n2", "name": "Bob"}]
    edges = [{"source": "n1", "target": "n2", "type": "KNOWS"}]
    assert algo.match_simple_path(nodes, edges, rel_type="KNOWS")["match_count"] == 1

def test_gql_evaluator():
    algo = KgAlgoGqlEvaluator()
    nodes = [{"id": "n1", "labels": ["Person"], "properties": {"age": 30}}]
    assert algo.filter_nodes_by_label_and_props(nodes, "Person")["count"] == 1

def test_gremlin_traversal():
    edges = [{"source": "v1", "target": "v2", "type": "knows"}]
    t = KgAlgoGremlinTraversal(edges, ["v1"])
    assert t.out("knows").to_list() == ["v2"]

def test_vf2_subgraph():
    algo = KgAlgoVf2SubgraphIsomorphism()
    pattern = [("p1", "p2")]
    target = [("t1", "t2"), ("t2", "t3")]
    assert algo.match(pattern, target)["mapping_count"] >= 1

def test_leapfrog_triejoin():
    algo = KgAlgoLeapfrogTriejoin()
    assert algo.leapfrog_intersect([[1, 5, 10], [5, 10, 15]]) == [5, 10]

def test_join_ordering():
    algo = KgAlgoJoinOrderingCardinality()
    res = algo.optimize_plan({"p_large": 1000, "p_small": 5})
    assert res["ordered_plan"][0] == "p_small"

def test_regular_path_queries():
    algo = KgAlgoRegularPathQueries()
    triples = [{"subject": "a", "predicate": "subClassOf", "object": "b"}, {"subject": "b", "predicate": "subClassOf", "object": "c"}]
    assert "c" in algo.evaluate_plus_path(triples, "a", "subClassOf")["reachable_nodes"]

def test_federated_queries():
    algo = KgAlgoFederatedQueries()
    results = {"ep1": [{"id": 1, "name": "Alice"}], "ep2": [{"id": 1, "dept": "AI"}]}
    assert algo.merge_federated_results(results, "id")["total_joined"] == 1

def test_obda_query_rewriting():
    algo = KgAlgoObdaQueryRewriting()
    sub_map = {"Employee": ["Engineer", "Manager"]}
    assert "Engineer" in algo.rewrite_concept_query("Employee", sub_map)["rewritten_union_queries"]

def test_parameterized_templates():
    algo = KgAlgoParameterizedTemplates()
    res = algo.render_query("MATCH (n {name: $name}) RETURN n", {"name": "Alice"})
    assert '"Alice"' in res["rendered_query"]

def test_pagination_caching():
    algo = KgAlgoPaginationCaching()
    items = list(range(25))
    page = algo.paginate(items, offset=0, limit=10)
    assert len(page["page_items"]) == 10
    assert page["has_more"] is True

# ==================== 6. ANALYTICS TESTS ====================

def test_bfs_traversal():
    algo = KgAlgoBfsTraversal()
    adj = {"A": ["B"], "B": ["C"]}
    assert "C" in algo.traverse(adj, "A", max_depth=2)["visited_nodes"]

def test_dfs_traversal():
    algo = KgAlgoDfsTraversal()
    adj = {"A": ["B"], "B": ["C"]}
    assert len(algo.traverse(adj, "A")["traversal_order"]) == 3

def test_bidirectional_bfs():
    algo = KgAlgoBidirectionalBfs()
    fwd = {"A": ["B"], "B": ["C"]}; rev = {"C": ["B"], "B": ["A"]}
    assert algo.find_shortest_path(fwd, rev, "A", "C")["path_found"] is True

def test_dijkstra_shortest_path():
    algo = KgAlgoDijkstraShortestPath()
    adj = {"A": [("B", 1.0), ("C", 4.0)], "B": [("C", 2.0)]}
    assert algo.compute_distances(adj, "A")["distances"]["C"] == 3.0

def test_astar_search():
    algo = KgAlgoAstarSearch()
    adj = {"A": [("B", 1.0), ("C", 5.0)], "B": [("C", 1.0)]}
    h = {"A": 2.0, "B": 1.0, "C": 0.0}
    res = algo.search(adj, h, "A", "C")
    assert res["found"] is True
    assert res["cost"] == 2.0
    assert res["path"] == ["A", "B", "C"]


def test_astar_search_generic_custom_model():
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class CustomNode:
        id: str
        x: float
        y: float

    algo = KgAlgoAstarSearch()
    n1 = CustomNode("n1", 0.0, 0.0)
    n2 = CustomNode("n2", 1.0, 1.0)
    n3 = CustomNode("n3", 2.0, 2.0)

    # Simulated database / custom lazy expansion
    def lazy_db_neighbors(node: CustomNode):
        if node.id == "n1":
            return [(n2, 1.5), (n3, 10.0)]
        elif node.id == "n2":
            return [(n3, 1.5)]
        return []

    # Dynamic Euclidean distance heuristic
    def euclidean_heuristic(node: CustomNode):
        return ((node.x - n3.x) ** 2 + (node.y - n3.y) ** 2) ** 0.5

    res = algo.search_generic(
        source=n1,
        target=n3,
        get_neighbors=lazy_db_neighbors,
        heuristic_fn=euclidean_heuristic,
        key_fn=lambda n: n.id,
    )
    assert res["found"] is True
    assert res["cost"] == 3.0
    assert [n.id for n in res["path"]] == ["n1", "n2", "n3"]


def test_astar_neo4j_query_builders():
    algo = KgAlgoAstarSearch()
    gds = algo.build_neo4j_gds_query("myGraph", "A", "B")
    assert "FLOW_GET_PROJECTED_ASTAR_SHORTEST_PATH" in gds["query_name"]
    assert gds["params"]["source_id"] == "A"

    apoc = algo.build_neo4j_apoc_query("A", "B")
    assert "FLOW_GET_PROCEDURE_ASTAR_SHORTEST_PATH" in apoc["query_name"]
    assert apoc["params"]["target_id"] == "B"


def test_astar_search_with_graph_store_adapter():
    from src.domain.ports.graph_port import GraphStorePort, GraphNode, GraphRelationship, GraphQueryResult

    class MockThirdPartyGraphDatabaseAdapter(GraphStorePort):
        def __init__(self):
            self.graph = {
                "S1": [GraphNode(id="S2", label="Service", properties={"weight": 1.2})],
                "S2": [GraphNode(id="S3", label="Service", properties={"weight": 2.5})],
                "S3": [],
            }

        def find_neighbors(self, node_id: str, rel_type=None, direction="OUTGOING"):
            return self.graph.get(node_id, [])

        def upsert_node(self, node): pass
        def upsert_relationship(self, relationship): pass
        def query_cypher(self, query, parameters=None): return GraphQueryResult()
        def find_shortest_path(self, start_id, end_id): return []
        def count_nodes(self): return 3
        def count_relationships(self): return 2
        def clear(self): pass
        def get_node(self, node_id): return None
        def find_node(self, query): return None
        def delete_node(self, node_id): return True
        def get_incoming_relationships(self, node_id): return []
        def get_outgoing_relationships(self, node_id): return []

    adapter = MockThirdPartyGraphDatabaseAdapter()
    algo = KgAlgoAstarSearch()
    res = algo.search_with_store(store=adapter, source_id="S1", target_id="S3")
    assert res["found"] is True
    assert res["cost"] == 3.7
    assert res["path"] == ["S1", "S2", "S3"]




def test_yens_k_shortest_paths():
    algo = KgAlgoYensKShortestPaths()
    adj = {"A": [("B", 1.0), ("C", 3.0)], "B": [("C", 1.0)]}
    assert len(algo.find_k_paths(adj, "A", "C", k=2)["paths"]) >= 1

def test_random_walk_restart():
    algo = KgAlgoRandomWalkRestart()
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["A"]}
    assert len(algo.run_walk(adj, "A", num_steps=50)["visit_frequencies"]) >= 1

def test_metapath_traversal():
    algo = KgAlgoMetapathTraversal()
    edges = [{"source": "u1", "type": "writes", "target": "p1"}, {"source": "p1", "type": "cites", "target": "p2"}]
    res = algo.traverse_metapath(edges, ["u1"], ["writes", "cites"])
    assert res["target_nodes"] == ["p2"]

def test_two_hop_labeling():
    algo = KgAlgoTwoHopLabeling()
    l_out = {"u": {"h1"}}; l_in = {"v": {"h1"}}
    assert algo.is_reachable(l_out, l_in, "u", "v") is True

def test_transitive_closure():
    algo = KgAlgoTransitiveClosure()
    adj = {"A": ["B"], "B": ["C"]}
    assert "C" in algo.compute_closure(adj)["reachability_map"]["A"]

def test_degree_centrality():
    algo = KgAlgoDegreeCentrality()
    res = algo.compute_centrality(["A", "B"], [("A", "B")])
    assert res["out_degrees"]["A"] == 1

def test_pagerank():
    algo = KgAlgoPagerankCentrality()
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    assert len(algo.compute_pagerank(nodes, edges)["scores"]) == 3

def test_personalized_pagerank():
    algo = KgAlgoPersonalizedPagerank()
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C")]
    res = algo.compute_ppr(nodes, edges, seed_nodes=["A"])
    assert res["ppr_scores"]["A"] > 0

def test_brandes_betweenness():
    algo = KgAlgoBrandesBetweenness()
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C")]
    assert algo.compute_betweenness(nodes, edges)["betweenness"]["B"] >= 0

def test_closeness_harmonic():
    algo = KgAlgoClosenessHarmonic()
    assert algo.compute_harmonic(["A", "B"], [("A", "B")])["harmonic_scores"]["A"] > 0

def test_hits_centrality():
    algo = KgAlgoHitsCentrality()
    res = algo.compute_hits(["A", "B"], [("A", "B")])
    assert "A" in res["hubs"]

def test_connected_components():
    algo = KgAlgoConnectedComponents()
    assert algo.find_components(["A", "B", "C"], [("A", "B")])["component_count"] == 2


def test_connected_components_generic_and_store():
    algo = KgAlgoConnectedComponents()
    nodes = ["N1", "N2", "N3", "N4"]
    adj = {"N1": ["N2"], "N2": ["N1"], "N3": ["N4"], "N4": ["N3"]}
    res = algo.find_components_generic(nodes=nodes, neighbor_provider=lambda n: adj.get(n, []))
    assert res["component_count"] == 2
    q = algo.build_cypher_query("my_graph")
    assert q["query_name"] == "FLOW_GET_CONNECTED_COMPONENTS"


def test_tarjan_scc():
    algo = KgAlgoTarjanScc()
    assert algo.compute_scc(["A", "B"], [("A", "B"), ("B", "A")])["scc_count"] == 1


def test_tarjan_scc_generic_and_store():
    algo = KgAlgoTarjanScc()
    nodes = ["1", "2", "3"]
    adj = {"1": ["2"], "2": ["1"], "3": []}
    res = algo.compute_scc_generic(nodes=nodes, get_outgoing=lambda n: adj.get(n, []))
    assert res["scc_count"] == 2
    q = algo.build_cypher_query("my_graph")
    assert q["query_name"] == "FLOW_GET_STRONGLY_CONNECTED_COMPONENTS"


def test_louvain_community():
    algo = KgAlgoLouvainCommunity()
    assert algo.detect_communities(["A", "B", "C", "D"], [("A", "B"), ("C", "D")])["community_count"] >= 2


def test_louvain_community_generic_and_store():
    algo = KgAlgoLouvainCommunity()
    nodes = ["A", "B", "C", "D"]
    adj = {"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"]}
    res = algo.detect_communities_generic(nodes=nodes, neighbor_provider=lambda n: adj.get(n, []))
    assert res["community_count"] == 2
    q = algo.build_cypher_query("my_graph")
    assert q["query_name"] == "FLOW_GET_LOUVAIN_COMMUNITIES"


def test_leiden_community():
    algo = KgAlgoLeidenCommunity()
    assert algo.refine_communities(["A", "B", "C", "D"], [("A", "B"), ("C", "D")])["community_count"] >= 2


def test_leiden_community_generic_and_store():
    algo = KgAlgoLeidenCommunity()
    nodes = ["A", "B", "C", "D"]
    adj = {"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"]}
    res = algo.refine_communities_generic(nodes=nodes, neighbor_provider=lambda n: adj.get(n, []))
    assert res["community_count"] == 2
    q = algo.build_cypher_query("my_graph")
    assert q["query_name"] == "FLOW_GET_LEIDEN_COMMUNITIES"


def test_label_propagation():
    algo = KgAlgoLabelPropagation()
    res = algo.propagate_labels(["A", "B"], [("A", "B")], initial_labels={"A": "red"})
    assert res["assigned_labels"]["B"] == "red"


def test_label_propagation_generic_and_store():
    algo = KgAlgoLabelPropagation()
    nodes = ["A", "B", "C"]
    adj = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    res = algo.propagate_labels_generic(
        nodes=nodes,
        neighbor_provider=lambda n: adj.get(n, []),
        initial_labels={"A": "team1", "C": "team2"},
    )
    assert res["assigned_labels"]["A"] == "team1"
    assert res["assigned_labels"]["C"] == "team2"
    q = algo.build_cypher_query("my_graph")
    assert q["query_name"] == "FLOW_GET_LABEL_PROPAGATION"


def test_k_core_decomposition():
    algo = KgAlgoKCoreDecomposition()
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")]
    assert len(algo.extract_k_core(nodes, edges, k=2)["k_core_nodes"]) == 3


def test_k_core_decomposition_generic_and_store():
    algo = KgAlgoKCoreDecomposition()
    nodes = ["A", "B", "C", "D"]
    adj = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B", "D"], "D": ["C"]}
    res = algo.extract_k_core_generic(nodes=nodes, neighbor_provider=lambda n: adj.get(n, []), k=2)
    assert res["k_core_size"] == 3
    assert "D" not in res["k_core_nodes"]
    q = algo.build_cypher_query("my_graph", k=2)
    assert q["query_name"] == "FLOW_GET_K_CORE_DECOMPOSITION"


def test_hits_centrality_generic_and_store():
    algo = KgAlgoHitsCentrality()
    nodes = ["A", "B"]
    out_adj = {"A": ["B"], "B": []}
    in_adj = {"A": [], "B": ["A"]}
    res = algo.compute_hits_generic(
        nodes=nodes,
        get_outgoing=lambda n: out_adj.get(n, []),
        get_incoming=lambda n: in_adj.get(n, []),
    )
    assert res["hubs"]["A"] > 0
    q = algo.build_cypher_query("my_graph")
    assert q["query_name"] == "FLOW_GET_HITS_CENTRALITY"


def test_random_walk_restart_generic():
    algo = KgAlgoRandomWalkRestart()
    adj = {"A": ["B"], "B": ["C"], "C": ["A"]}
    res = algo.run_walk_generic(start_node="A", neighbor_provider=lambda n: adj.get(n, []), num_steps=50, seed=42)
    assert len(res["visit_frequencies"]) >= 1
    q = algo.build_cypher_query("my_graph", start_node="A")
    assert q["query_name"] == "FLOW_GET_RANDOM_WALK_RESTART"


def test_metapath_traversal_generic():
    algo = KgAlgoMetapathTraversal()
    def typed_nbrs(node: str, rel: str):
        if node == "user1" and rel == "wrote":
            return ["paper1"]
        if node == "paper1" and rel == "cited":
            return ["paper2"]
        return []

    res = algo.traverse_metapath_generic(
        start_nodes=["user1"],
        get_typed_neighbors=typed_nbrs,
        metapath=["wrote", "cited"],
    )
    assert res["target_nodes"] == ["paper2"]
    q = algo.build_cypher_query("user1", ["wrote", "cited"])
    assert q["query_name"] == "FLOW_GET_METAPATH_TRAVERSAL"


def test_two_hop_labeling_generic():
    algo = KgAlgoTwoHopLabeling()
    l_out = {"u1": {"hub1"}}
    l_in = {"v1": {"hub1"}}
    assert algo.is_reachable_generic(l_out, l_in, "u1", "v1") is True
    assert algo.is_reachable_generic(l_out, l_in, "u1", "v2") is False
    q = algo.build_cypher_query("u1", "v1")
    assert q["query_name"] == "FLOW_GET_TWO_HOP_REACHABILITY"


def test_transitive_closure_generic():
    algo = KgAlgoTransitiveClosure()
    adj = {"A": ["B"], "B": ["C"], "C": []}
    res = algo.compute_closure_generic(nodes=["A", "B", "C"], neighbor_provider=lambda n: adj.get(n, []))
    assert res["reachability_map"]["A"] == ["B", "C"]
    assert res["reachability_map"]["B"] == ["C"]
    assert res["reachability_map"]["C"] == []
    q = algo.build_cypher_query("A")
    assert q["query_name"] == "FLOW_GET_TRANSITIVE_CLOSURE"


# ==================== 7. REASONING TESTS ====================

def test_rdfs_entailment():
    algo = KgAlgoRdfsEntailment()
    triples = [{"subject": "writesCode", "predicate": "rdfs:subPropertyOf", "object": "develops"}, {"subject": "Alice", "predicate": "writesCode", "object": "App"}]
    res = algo.apply_entailment(triples)
    assert any(t["predicate"] == "develops" for t in res["inferred_triples"])

def test_owl2_rl_reasoner():
    algo = KgAlgoOwl2RlReasoner()
    triples = [{"subject": "parentOf", "predicate": "owl:inverseOf", "object": "childOf"}, {"subject": "Alice", "predicate": "parentOf", "object": "Bob"}]
    res = algo.infer_rl_axioms(triples)
    assert any(t["predicate"] == "childOf" for t in res["inferred_facts"])

def test_rete_forward_chaining():
    algo = KgAlgoReteForwardChaining()
    wm = [{"entity": "Alice", "role": "Admin"}]
    rules = [{"if_field": "role", "if_value": "Admin", "then": {"has_root_access": True}}]
    assert algo.forward_chain(wm, rules)["derived_facts"][0]["has_root_access"] is True

def test_backward_chaining():
    algo = KgAlgoBackwardChaining()
    known = {"has_license"}
    rules = [{"head": "can_drive", "name": "drive_rule", "body": ["has_license"]}]
    assert algo.prove_goal(known, rules, "can_drive")["proved"] is True

def test_datalog_semi_naive():
    algo = KgAlgoDatalogSemiNaive()
    edges = [("a", "b"), ("b", "c")]
    assert ("a", "c") in algo.compute_transitive_path(edges)["idb_facts"]

def test_materialization_planner():
    algo = KgAlgoMaterializationPlanner()
    assert "MATERIALIZATION" in algo.plan_strategy(read_qps=1000, write_qps=2, graph_size=10000)["recommended_strategy"]

def test_dred_incremental():
    algo = KgAlgoDredIncrementalMaintenance()
    base = {"f1", "f2"}
    derived = {"f3": ["f1", "f2"]}
    assert "f3" not in algo.maintain_deletion(base, derived, "f1")["remaining_facts"]

def test_same_as_congruence():
    algo = KgAlgoSameAsCongruence()
    assert algo.apply_equality([("id1", "id2")], [{"subject": "id2", "predicate": "knows", "object": "Bob"}])["canonical_triples"][0]["subject"] == "id1"

def test_tableau_reasoner():
    algo = KgAlgoTableauReasoner()
    assertions = {"ind1": {"Person", "not_Person"}}
    assert algo.check_satisfiability(assertions)["satisfiable"] is False

def test_owl2_el_classification():
    algo = KgAlgoOwl2ElClassification()
    axioms = [("HeartDisease", "CardiovascularDisease"), ("CardiovascularDisease", "Disease")]
    assert "Disease" in algo.classify(axioms)["classified_hierarchy"]["HeartDisease"]

def test_amie_rule_mining():
    algo = KgAlgoAmieRuleMining()
    triples = [{"subject": "Alice", "predicate": "marriedTo", "object": "Bob"}, {"subject": "Bob", "predicate": "marriedTo", "object": "Alice"}]
    assert algo.mine_inverse_rules(triples)["rule_count"] >= 1

def test_open_closed_world():
    algo = KgAlgoOpenClosedWorld()
    res = algo.evaluate_fact_existence({"sky_is_blue"}, "sky_is_green")
    assert "Negation" in res["cwa_result"]
    assert "UNKNOWN" in res["owa_result"]

def test_inconsistency_justification():
    algo = KgAlgoInconsistencyJustification()
    facts = [{"subject": "X", "predicate": "rdf:type", "object": "Male"}, {"subject": "X", "predicate": "rdf:type", "object": "Female"}]
    assert algo.find_minimal_justifications(facts, ("Male", "Female"))["justification_count"] == 1

def test_probabilistic_soft_logic():
    algo = KgAlgoProbabilisticSoftLogic()
    res = algo.evaluate_lukasiewicz_operators(0.8, 0.7)
    assert res["conjunction"] == 0.5

def test_allens_interval_algebra():
    algo = KgAlgoAllensIntervalAlgebra()
    assert algo.determine_relation((1.0, 5.0), (6.0, 10.0)) == "BEFORE"

def test_inconsistency_repair():
    algo = KgAlgoInconsistencyRepair()
    facts = [{"subject": "A", "type": "Herbivore", "confidence": 0.9}, {"subject": "A", "type": "Carnivore", "confidence": 0.3}]
    assert algo.repair_conflicts(facts, [("Herbivore", "Carnivore")])["repaired_facts_count"] == 1
