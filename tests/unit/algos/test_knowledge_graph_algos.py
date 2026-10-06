"""
================================================================================
UNIT TESTS: KNOWLEDGE GRAPH MODELING, STORAGE & CONSTRUCTION (PART 1, #1–50)
================================================================================
"""

import pytest
from src.features.code_engine.algos.knowledge_graph import (
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
    KgAlgoAdjacencyList,
    KgAlgoCsrRepresentation,
    KgAlgoIndexFreeAdjacency,
    KgAlgoHexastorePermutation,
    KgAlgoDictionaryEncoding,
    KgAlgoBtreeLsmStorage,
    KgAlgoCompressedHdt,
    KgAlgoGraphPartitioning,
    KgAlgoHashPartitioning,
    KgAlgoPropertyFulltextIndex,
    KgAlgoHybridGraphVector,
    KgAlgoGraphSnapshotsMvcc,
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
    KgAlgoEntityResolutionBlocking,
    KgAlgoFellegiSunterLinkage,
    KgAlgoSimilarityJoins,
    KgAlgoMatchClustering,
    KgAlgoEntityCanonicalization,
    KgAlgoRelationCanonicalization,
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
)


def test_rdf_triples():
    algo = KgAlgoRdfTriples()
    nt = "<http://example.org/Alice> <http://xmlns.com/foaf/0.1/knows> <http://example.org/Bob> .\n"
    res = algo.parse_ntriples(nt)
    assert res["triple_count"] == 1
    assert res["triples"][0]["subject"] == "http://example.org/Alice"


def test_rdfs_schema():
    algo = KgAlgoRdfsSchema()
    sub_classes = [{"child": "Dog", "parent": "Mammal"}, {"child": "Mammal", "parent": "Animal"}]
    instances = [{"entity": "Fido", "class": "Dog"}]
    res = algo.infer_hierarchy(sub_classes, instances)
    inferred_types = {t["inferred_class"] for t in res["inferred_types"]}
    assert "Animal" in inferred_types
    assert "Mammal" in inferred_types


def test_owl2_ontology():
    algo = KgAlgoOwl2Ontology()
    facts = [
        {"subject": "urn:person1", "predicate": "type", "object": "Male"},
        {"subject": "urn:person1", "predicate": "type", "object": "Female"},
    ]
    res = algo.check_axioms(facts, disjoint_pairs=[("Male", "Female")], functional_props=[])
    assert res["valid"] is False
    assert len(res["violations"]) == 1


def test_labeled_property_graph():
    lpg = KgAlgoLabeledPropertyGraph()
    lpg.add_node("n1", ["User"], {"name": "Alice"})
    lpg.add_node("n2", ["Organization"], {"name": "TechCorp"})
    lpg.add_edge("n1", "n2", "MEMBER_OF", {"role": "Engineer"})
    data = lpg.to_graph_data()
    assert data["node_count"] == 2
    assert data["edge_count"] == 1


def test_shacl_shapes():
    algo = KgAlgoShaclShapes()
    nodes = [{"id": "n1", "labels": ["User"], "properties": {"name": "Alice", "age": 30}}]
    shapes = [{"target_class": "User", "property_shapes": [{"path": "name", "min_count": 1, "datatype": "string"}]}]
    res = algo.validate_shapes(nodes, shapes)
    assert res["conforms"] is True


def test_skos_concept():
    algo = KgAlgoSkosConcept()
    relations = [{"subject": "ML", "predicate": "skos:broader", "object": "AI"}]
    res = algo.build_taxonomy(relations)
    assert "AI" in res["top_concepts"]


def test_jsonld_processor():
    algo = KgAlgoJsonLdProcessor()
    doc = {"@context": {"name": "schema:name"}, "name": "Alice"}
    res = algo.expand_document(doc)
    assert res["expanded_nodes"][0]["schema:name"] == "Alice"


def test_iri_namespaces():
    algo = KgAlgoIriNamespaces()
    expanded = algo.expand_curie("schema:Person")
    assert expanded == "https://schema.org/Person"
    compacted = algo.compact_iri("https://schema.org/Person")
    assert compacted == "schema:Person"


def test_rdf_star_reification():
    algo = KgAlgoRdfStarReification()
    res = algo.reify_triple("Alice", "knows", "Bob", {"confidence": 0.95})
    assert res["quoted_triple"] == "<< Alice knows Bob >>"
    assert len(res["reified_triples"]) >= 5


def test_named_graphs_quads():
    algo = KgAlgoNamedGraphsQuads()
    algo.add_quad("Alice", "knows", "Bob", "urn:graph:social")
    stats = algo.get_dataset_stats()
    assert stats["total_quads"] == 1
    assert "urn:graph:social" in stats["graph_names"]


def test_schema_org_mapper():
    algo = KgAlgoSchemaOrgMapper()
    res = algo.map_entity_to_schema_org({"type": "user", "name": "Alice", "email": "alice@test.com"})
    assert res["schema_type"] == "schema:Person"
    assert res["mapped_entity"]["schema:name"] == "Alice"


def test_bitemporal_modeling():
    algo = KgAlgoBitemporalModeling()
    facts = [{
        "fact": "Alice is CEO",
        "valid_from": 100.0,
        "valid_to": 200.0,
        "tx_from": 50.0,
        "tx_to": float("inf"),
    }]
    res = algo.query_as_of(facts, valid_at=150.0, system_at=100.0)
    assert res["active_facts_count"] == 1


def test_adjacency_list():
    algo = KgAlgoAdjacencyList()
    algo.add_edge("A", "B", "friend")
    neighbors = algo.get_neighbors("A", "out")
    assert len(neighbors) == 1
    assert neighbors[0]["target"] == "B"


def test_csr_representation():
    algo = KgAlgoCsrRepresentation()
    edges = [(0, 1), (0, 2), (1, 2)]
    res = algo.build_csr(3, edges)
    assert res["num_edges"] == 3
    assert len(res["row_offsets"]) == 4


def test_index_free_adjacency():
    from src.features.code_engine.algos.knowledge_graph.kg_algo_index_free_adjacency import (
        KgPointerNode,
        KgPointerEdge,
        KgAlgoIndexFreeAdjacency,
    )
    algo = KgAlgoIndexFreeAdjacency()
    n1 = KgPointerNode("A")
    n2 = KgPointerNode("B")
    e = KgPointerEdge(n1, n2, "points_to")
    n1.first_outgoing = e
    res = algo.traverse_outgoing(n1)
    assert len(res) == 1
    assert res[0]["target"] == "B"


def test_hexastore_permutation():
    algo = KgAlgoHexastorePermutation()
    algo.insert_triple("Alice", "knows", "Bob")
    res = algo.query(s="Alice", p="knows")
    assert len(res) == 1
    assert res[0] == ("Alice", "knows", "Bob")


def test_dictionary_encoding():
    algo = KgAlgoDictionaryEncoding()
    triples = [("Alice", "knows", "Bob")]
    encoded = algo.encode_triples(triples)
    assert len(encoded) == 1
    assert algo.decode(encoded[0][0]) == "Alice"


def test_btree_lsm_storage():
    algo = KgAlgoBtreeLsmStorage(max_memtable_size=2)
    algo.put_fact("fact1", "active")
    algo.put_fact("fact2", "active")
    assert algo.get_fact("fact1") == "active"


def test_compressed_hdt():
    algo = KgAlgoCompressedHdt()
    triples = [("Alice", "knows", "Bob")]
    res = algo.encode_hdt(triples, {"source": "test"})
    assert res["total_triples"] == 1


def test_graph_partitioning():
    algo = KgAlgoGraphPartitioning()
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B"), ("C", "D"), ("B", "C")]
    res = algo.partition_edge_cut(nodes, edges, num_partitions=2)
    assert res["num_partitions"] == 2


def test_hash_partitioning():
    algo = KgAlgoHashPartitioning()
    res = algo.assign_nodes_and_edges(["A", "B"], [("A", "B")], num_shards=2)
    assert "A" in res["node_assignments"]


def test_property_fulltext_index():
    algo = KgAlgoPropertyFulltextIndex()
    algo.index_node("node_1", {"title": "Fast Neural Knowledge Graphs"})
    hits = algo.search("Neural Knowledge")
    assert hits == ["node_1"]


def test_hybrid_graph_vector():
    algo = KgAlgoHybridGraphVector()
    algo.add_vector("n1", [1.0, 0.0])
    algo.add_vector("n2", [0.0, 1.0])
    hits = algo.search_similar_nodes([1.0, 0.0], top_k=1)
    assert hits[0]["node_id"] == "n1"


def test_graph_snapshots_mvcc():
    algo = KgAlgoGraphSnapshotsMvcc()
    snap = algo.commit_snapshot({"entity_1": "v1"}, author="engineer")
    assert snap["snapshot_id"] == "v_1"
    state = algo.get_snapshot("v_1")
    assert state["entity_1"] == "v1"


def test_text_segmentation():
    algo = KgAlgoTextSegmentation()
    res = algo.segment_text("First sentence. Second sentence!")
    assert res["sentence_count"] == 2


def test_named_entity_recognition():
    algo = KgAlgoNamedEntityRecognition()
    res = algo.extract_entities("Dr. Alan Turing founded Turing Corp in London.")
    assert res["entity_count"] >= 1


def test_entity_linking():
    algo = KgAlgoEntityLinking()
    kb = {"kb_apple": {"name": "Apple", "aliases": ["Apple Inc."]}}
    res = algo.link_entities([{"text": "Apple Inc."}], kb)
    assert res["linked_results"][0]["kb_id"] == "kb_apple"


def test_coreference_resolution():
    algo = KgAlgoCoreferenceResolution()
    res = algo.resolve_pronouns(["Alice visited London.", "She liked the museum."])
    assert "[Alice]" in res["resolved_sentences"][1]


def test_supervised_relation_extraction():
    algo = KgAlgoSupervisedRelationExtraction()
    res = algo.extract_relations("Alice founded TechCorp today.")
    assert len(res["relations"]) == 1
    assert res["relations"][0]["predicate"] == "founded"


def test_open_information_extraction():
    algo = KgAlgoOpenInformationExtraction()
    res = algo.extract_open_triples("Alice loves Python")
    assert res["triple_count"] >= 1


def test_llm_schema_extraction():
    algo = KgAlgoLlmSchemaExtraction()
    raw = {
        "entities": [{"text": "Alice", "type": "Person"}, {"text": "Unknown", "type": "Alien"}],
        "relations": [{"subject": "Alice", "predicate": "knows", "object": "Bob"}],
    }
    res = algo.extract_with_schema(raw, ["Person"], ["knows"])
    assert len(res["extracted_entities"]) == 1


def test_event_extraction():
    algo = KgAlgoEventExtraction()
    res = algo.extract_event("Acquisition", "BusinessEvent", [{"role": "buyer", "entity": "TechCorp"}], "2026-01-01", "NYC")
    assert res["event_type"] == "BusinessEvent"


def test_attribute_normalization():
    algo = KgAlgoAttributeNormalization()
    res = algo.normalize_value("250 MB")
    assert res["normalized_value"] == 250.0
    assert res["unit"] == "mb"


def test_structured_table_extraction():
    algo = KgAlgoStructuredTableExtraction()
    rows = [{"id": 1, "name": "Alice", "role": "Admin"}]
    res = algo.table_to_triples(rows, "id", "User")
    assert res["triple_count"] == 3


def test_entity_resolution_blocking():
    algo = KgAlgoEntityResolutionBlocking()
    records = [{"id": 1, "name": "Robert"}, {"id": 2, "name": "Rob"}, {"id": 3, "name": "Alice"}]
    blocks = algo.generate_blocks(records, "name")
    assert len(blocks["rob"]) == 2


def test_fellegi_sunter_linkage():
    algo = KgAlgoFellegiSunterLinkage()
    rec_a = {"name": "Alice", "zip": "90210"}
    rec_b = {"name": "Alice", "zip": "90210"}
    res = algo.evaluate_pair(rec_a, rec_b, ["name", "zip"], threshold=1.0)
    assert res["is_match"] is True


def test_similarity_joins():
    algo = KgAlgoSimilarityJoins()
    list_a = [{"id": 1, "title": "deep learning for graphs"}]
    list_b = [{"id": 2, "title": "deep learning for knowledge graphs"}]
    matches = algo.join_pairs(list_a, list_b, "title", min_similarity=0.6)
    assert len(matches) == 1


def test_match_clustering():
    algo = KgAlgoMatchClustering()
    pairs = [("A", "B"), ("B", "C"), ("D", "E")]
    res = algo.cluster_pairs(pairs)
    assert res["cluster_count"] == 2


def test_entity_canonicalization():
    algo = KgAlgoEntityCanonicalization()
    records = [
        {"name": "Robert Smith", "city": "NYC"},
        {"name": "Rob Smith", "city": "NYC"},
        {"name": "Robert Smith", "city": "New York"},
    ]
    res = algo.synthesize_golden_record(records)
    assert res["golden_record"]["name"] == "Robert Smith"
    assert res["golden_record"]["city"] == "NYC"


def test_relation_canonicalization():
    algo = KgAlgoRelationCanonicalization()
    triples = [{"subject": "Alice", "predicate": "bought", "object": "Book"}]
    res = algo.canonicalize_triples(triples)
    assert res["canonical_triples"][0]["predicate"] == "acquired"


def test_ontology_alignment():
    algo = KgAlgoOntologyAlignment()
    res = algo.align_concepts(["ont1:Person"], ["ont2:Person"])
    assert len(res) == 1
    assert res[0]["similarity"] == 1.0


def test_r2rml_schema_mapping():
    algo = KgAlgoR2rmlSchemaMapping()
    data = [{"emp_id": 101, "name": "Alice"}]
    spec = {
        "subject_template": "urn:emp:{emp_id}",
        "predicate_object_maps": [{"predicate": "schema:name", "column": "name"}],
    }
    res = algo.apply_mapping(data, spec)
    assert res["count"] == 1
    assert res["generated_triples"][0]["subject"] == "urn:emp:101"


def test_taxonomy_hearst_induction():
    algo = KgAlgoTaxonomyHearstInduction()
    res = algo.extract_hypernyms("Programming languages such as Python, Rust, Go are popular.")
    assert len(res) >= 1
    assert res[0]["parent"] == "languages"


def test_entity_type_inference():
    algo = KgAlgoEntityTypeInference()
    triples = [{"subject": "Alice", "predicate": "writesCodeFor", "object": "TechCorp"}]
    schema = {"writesCodeFor": {"domain": "Developer", "range": "Company"}}
    res = algo.infer_types(triples, schema)
    types = {i["entity"]: i["inferred_type"] for i in res["inferences"]}
    assert types["Alice"] == "Developer"
    assert types["TechCorp"] == "Company"


def test_llm_ontology_synthesis():
    algo = KgAlgoLlmOntologySynthesis()
    res = algo.synthesize_ontology("FinTech", ["Account", "Transaction"], ["transfersTo"])
    assert "FinTech".lower() in res["ontology_uri"]
    assert len(res["classes"]) == 2


def test_schema_evolution():
    algo = KgAlgoSchemaEvolution()
    v1 = {"classes": ["User", "Admin"]}
    v2 = {"classes": ["User", "Admin", "SuperAdmin"]}
    res = algo.check_compatibility(v1, v2)
    assert res["backward_compatible"] is True
    assert "SuperAdmin" in res["added_classes"]


def test_property_graph_constraints():
    algo = KgAlgoPropertyGraphConstraints()
    nodes = [
        {"id": "n1", "properties": {"email": "alice@test.com"}},
        {"id": "n2", "properties": {"email": "alice@test.com"}},
    ]
    res = algo.enforce_constraints(nodes, unique_properties=["email"], required_properties=["email"])
    assert res["valid"] is False


def test_data_quality_evaluator():
    algo = KgAlgoDataQualityEvaluator()
    nodes = [{"id": "n1", "labels": ["User"]}, {"id": "n2", "labels": ["Org"]}]
    edges = [{"source": "n1", "target": "n2"}]
    res = algo.evaluate_quality(nodes, edges)
    assert res["quality_grade"] == "HIGH"
    assert res["dangling_edges"] == 0


def test_relation_normalization():
    algo = KgAlgoRelationNormalization()
    triples = [{"subject": "Bob", "predicate": "siblingOf", "object": "Alice"}]
    res = algo.normalize_graph(triples)
    assert res["triples"][0]["subject"] == "Alice"
    assert res["triples"][0]["object"] == "Bob"


def test_truth_discovery_confidence():
    algo = KgAlgoTruthDiscoveryConfidence()
    claims = [
        {"subject": "Earth", "predicate": "shape", "object": "Sphere", "source": "NASA"},
        {"subject": "Earth", "predicate": "shape", "object": "Flat", "source": "Blog"},
    ]
    reliabilities = {"NASA": 0.99, "Blog": 0.1}
    res = algo.compute_fact_confidence(claims, reliabilities)
    assert "Sphere" in res["ranked_facts"][0]["fact"]
    assert res["ranked_facts"][0]["confidence"] > res["ranked_facts"][1]["confidence"]
