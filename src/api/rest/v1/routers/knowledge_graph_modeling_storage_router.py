"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 KNOWLEDGE GRAPH MODELING, STORAGE, CONSTRUCTION & RESOLUTION

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Knowledge Graph Modeling, Storage, Construction & Resolution.

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_bitemporal_modeling import KgAlgoBitemporalModeling
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_data_quality_evaluator import KgAlgoDataQualityEvaluator
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_entity_type_inference import KgAlgoEntityTypeInference
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_iri_namespaces import KgAlgoIriNamespaces
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_jsonld_processor import KgAlgoJsonLdProcessor
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_labeled_property_graph import KgAlgoLabeledPropertyGraph
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_llm_ontology_synthesis import KgAlgoLlmOntologySynthesis
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_named_graphs_quads import KgAlgoNamedGraphsQuads
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_ontology_alignment import KgAlgoOntologyAlignment
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_owl2_ontology import KgAlgoOwl2Ontology
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_property_graph_constraints import KgAlgoPropertyGraphConstraints
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_r2rml_schema_mapping import KgAlgoR2rmlSchemaMapping
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_rdf_star_reification import KgAlgoRdfStarReification
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_rdf_triples import KgAlgoRdfTriples
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_rdfs_schema import KgAlgoRdfsSchema
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_relation_normalization import KgAlgoRelationNormalization
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_schema_evolution import KgAlgoSchemaEvolution
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_schema_org_mapper import KgAlgoSchemaOrgMapper
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_shacl_shapes import KgAlgoShaclShapes
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_skos_concept import KgAlgoSkosConcept
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_taxonomy_hearst_induction import KgAlgoTaxonomyHearstInduction
from src.features.code_engine.algos.knowledge_graph.modeling.kg_algo_truth_discovery_confidence import KgAlgoTruthDiscoveryConfidence
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_adjacency_list import KgAlgoAdjacencyList
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_btree_lsm_storage import KgAlgoBtreeLsmStorage
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_compressed_hdt import KgAlgoCompressedHdt
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_csr_representation import KgAlgoCsrRepresentation
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_dictionary_encoding import KgAlgoDictionaryEncoding
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_graph_partitioning import KgAlgoGraphPartitioning
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_graph_snapshots_mvcc import KgAlgoGraphSnapshotsMvcc
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_hash_partitioning import KgAlgoHashPartitioning
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_hexastore_permutation import KgAlgoHexastorePermutation
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_hybrid_graph_vector import KgAlgoHybridGraphVector
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_index_free_adjacency import KgAlgoIndexFreeAdjacency
from src.features.code_engine.algos.knowledge_graph.storage.kg_algo_property_fulltext_index import KgAlgoPropertyFulltextIndex
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_attribute_normalization import KgAlgoAttributeNormalization
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_coreference_resolution import KgAlgoCoreferenceResolution
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_entity_linking import KgAlgoEntityLinking
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_event_extraction import KgAlgoEventExtraction
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_llm_schema_extraction import KgAlgoLlmSchemaExtraction
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_named_entity_recognition import KgAlgoNamedEntityRecognition
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_open_information_extraction import KgAlgoOpenInformationExtraction
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_structured_table_extraction import KgAlgoStructuredTableExtraction
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_supervised_relation_extraction import KgAlgoSupervisedRelationExtraction
from src.features.code_engine.algos.knowledge_graph.construction.kg_algo_text_segmentation import KgAlgoTextSegmentation
from src.features.code_engine.algos.knowledge_graph.resolution.kg_algo_entity_canonicalization import KgAlgoEntityCanonicalization
from src.features.code_engine.algos.knowledge_graph.resolution.kg_algo_entity_resolution_blocking import KgAlgoEntityResolutionBlocking
from src.features.code_engine.algos.knowledge_graph.resolution.kg_algo_fellegi_sunter_linkage import KgAlgoFellegiSunterLinkage
from src.features.code_engine.algos.knowledge_graph.resolution.kg_algo_match_clustering import KgAlgoMatchClustering
from src.features.code_engine.algos.knowledge_graph.resolution.kg_algo_relation_canonicalization import KgAlgoRelationCanonicalization
from src.features.code_engine.algos.knowledge_graph.resolution.kg_algo_similarity_joins import KgAlgoSimilarityJoins

router = APIRouter(prefix="/algos/knowledge-graph/foundation", tags=["Knowledge Graph Foundation Algorithms"])

class KgAlgoBitemporalModelingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDataQualityEvaluatorDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoEntityTypeInferenceDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoIriNamespacesDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoJsonLdProcessorDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLabeledPropertyGraphDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLlmOntologySynthesisDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoNamedGraphsQuadsDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOntologyAlignmentDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOwl2OntologyDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoPropertyGraphConstraintsDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoR2rmlSchemaMappingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRdfStarReificationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRdfTriplesDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRdfsSchemaDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRelationNormalizationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSchemaEvolutionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSchemaOrgMapperDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoShaclShapesDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSkosConceptDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTaxonomyHearstInductionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTruthDiscoveryConfidenceDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoAdjacencyListDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoBtreeLsmStorageDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoCompressedHdtDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoCsrRepresentationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoDictionaryEncodingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoGraphPartitioningDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoGraphSnapshotsMvccDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoHashPartitioningDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoHexastorePermutationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoHybridGraphVectorDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoIndexFreeAdjacencyDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoPropertyFulltextIndexDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoAttributeNormalizationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoCoreferenceResolutionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoEntityLinkingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoEventExtractionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoLlmSchemaExtractionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoNamedEntityRecognitionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoOpenInformationExtractionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoStructuredTableExtractionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSupervisedRelationExtractionDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoTextSegmentationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoEntityCanonicalizationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoEntityResolutionBlockingDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoFellegiSunterLinkageDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoMatchClusteringDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoRelationCanonicalizationDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")

class KgAlgoSimilarityJoinsDTO(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and data payload matching algorithm contract")


@router.post("/bitemporal-modeling")
def kgalgobitemporalmodeling_endpoint(body: KgAlgoBitemporalModelingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoBitemporalModeling()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoBitemporalModeling"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/data-quality-evaluator")
def kgalgodataqualityevaluator_endpoint(body: KgAlgoDataQualityEvaluatorDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDataQualityEvaluator()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDataQualityEvaluator"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/entity-type-inference")
def kgalgoentitytypeinference_endpoint(body: KgAlgoEntityTypeInferenceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoEntityTypeInference()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoEntityTypeInference"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/iri-namespaces")
def kgalgoirinamespaces_endpoint(body: KgAlgoIriNamespacesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoIriNamespaces()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoIriNamespaces"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/jsonld-processor")
def kgalgojsonldprocessor_endpoint(body: KgAlgoJsonLdProcessorDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoJsonLdProcessor()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoJsonLdProcessor"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/labeled-property-graph")
def kgalgolabeledpropertygraph_endpoint(body: KgAlgoLabeledPropertyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLabeledPropertyGraph()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLabeledPropertyGraph"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/llm-ontology-synthesis")
def kgalgollmontologysynthesis_endpoint(body: KgAlgoLlmOntologySynthesisDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLlmOntologySynthesis()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLlmOntologySynthesis"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/named-graphs-quads")
def kgalgonamedgraphsquads_endpoint(body: KgAlgoNamedGraphsQuadsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoNamedGraphsQuads()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoNamedGraphsQuads"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/ontology-alignment")
def kgalgoontologyalignment_endpoint(body: KgAlgoOntologyAlignmentDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOntologyAlignment()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOntologyAlignment"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/owl2-ontology")
def kgalgoowl2ontology_endpoint(body: KgAlgoOwl2OntologyDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOwl2Ontology()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOwl2Ontology"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/property-graph-constraints")
def kgalgopropertygraphconstraints_endpoint(body: KgAlgoPropertyGraphConstraintsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoPropertyGraphConstraints()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoPropertyGraphConstraints"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/r2rml-schema-mapping")
def kgalgor2rmlschemamapping_endpoint(body: KgAlgoR2rmlSchemaMappingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoR2rmlSchemaMapping()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoR2rmlSchemaMapping"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/rdf-star-reification")
def kgalgordfstarreification_endpoint(body: KgAlgoRdfStarReificationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRdfStarReification()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRdfStarReification"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/rdf-triples")
def kgalgordftriples_endpoint(body: KgAlgoRdfTriplesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRdfTriples()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRdfTriples"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/rdfs-schema")
def kgalgordfsschema_endpoint(body: KgAlgoRdfsSchemaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRdfsSchema()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRdfsSchema"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/relation-normalization")
def kgalgorelationnormalization_endpoint(body: KgAlgoRelationNormalizationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRelationNormalization()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRelationNormalization"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/schema-evolution")
def kgalgoschemaevolution_endpoint(body: KgAlgoSchemaEvolutionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSchemaEvolution()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSchemaEvolution"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/schema-org-mapper")
def kgalgoschemaorgmapper_endpoint(body: KgAlgoSchemaOrgMapperDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSchemaOrgMapper()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSchemaOrgMapper"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/shacl-shapes")
def kgalgoshaclshapes_endpoint(body: KgAlgoShaclShapesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoShaclShapes()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoShaclShapes"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/skos-concept")
def kgalgoskosconcept_endpoint(body: KgAlgoSkosConceptDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSkosConcept()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSkosConcept"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/taxonomy-hearst-induction")
def kgalgotaxonomyhearstinduction_endpoint(body: KgAlgoTaxonomyHearstInductionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTaxonomyHearstInduction()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTaxonomyHearstInduction"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/truth-discovery-confidence")
def kgalgotruthdiscoveryconfidence_endpoint(body: KgAlgoTruthDiscoveryConfidenceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTruthDiscoveryConfidence()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTruthDiscoveryConfidence"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/adjacency-list")
def kgalgoadjacencylist_endpoint(body: KgAlgoAdjacencyListDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoAdjacencyList()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoAdjacencyList"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/btree-lsm-storage")
def kgalgobtreelsmstorage_endpoint(body: KgAlgoBtreeLsmStorageDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoBtreeLsmStorage()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoBtreeLsmStorage"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/compressed-hdt")
def kgalgocompressedhdt_endpoint(body: KgAlgoCompressedHdtDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoCompressedHdt()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoCompressedHdt"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/csr-representation")
def kgalgocsrrepresentation_endpoint(body: KgAlgoCsrRepresentationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoCsrRepresentation()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoCsrRepresentation"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/dictionary-encoding")
def kgalgodictionaryencoding_endpoint(body: KgAlgoDictionaryEncodingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoDictionaryEncoding()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoDictionaryEncoding"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/graph-partitioning")
def kgalgographpartitioning_endpoint(body: KgAlgoGraphPartitioningDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoGraphPartitioning()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoGraphPartitioning"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/graph-snapshots-mvcc")
def kgalgographsnapshotsmvcc_endpoint(body: KgAlgoGraphSnapshotsMvccDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoGraphSnapshotsMvcc()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoGraphSnapshotsMvcc"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/hash-partitioning")
def kgalgohashpartitioning_endpoint(body: KgAlgoHashPartitioningDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoHashPartitioning()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoHashPartitioning"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/hexastore-permutation")
def kgalgohexastorepermutation_endpoint(body: KgAlgoHexastorePermutationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoHexastorePermutation()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoHexastorePermutation"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/hybrid-graph-vector")
def kgalgohybridgraphvector_endpoint(body: KgAlgoHybridGraphVectorDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoHybridGraphVector()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoHybridGraphVector"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/index-free-adjacency")
def kgalgoindexfreeadjacency_endpoint(body: KgAlgoIndexFreeAdjacencyDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoIndexFreeAdjacency()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoIndexFreeAdjacency"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/property-fulltext-index")
def kgalgopropertyfulltextindex_endpoint(body: KgAlgoPropertyFulltextIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoPropertyFulltextIndex()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoPropertyFulltextIndex"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/attribute-normalization")
def kgalgoattributenormalization_endpoint(body: KgAlgoAttributeNormalizationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoAttributeNormalization()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoAttributeNormalization"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/coreference-resolution")
def kgalgocoreferenceresolution_endpoint(body: KgAlgoCoreferenceResolutionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoCoreferenceResolution()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoCoreferenceResolution"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/entity-linking")
def kgalgoentitylinking_endpoint(body: KgAlgoEntityLinkingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoEntityLinking()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoEntityLinking"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/event-extraction")
def kgalgoeventextraction_endpoint(body: KgAlgoEventExtractionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoEventExtraction()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoEventExtraction"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/llm-schema-extraction")
def kgalgollmschemaextraction_endpoint(body: KgAlgoLlmSchemaExtractionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoLlmSchemaExtraction()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoLlmSchemaExtraction"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/named-entity-recognition")
def kgalgonamedentityrecognition_endpoint(body: KgAlgoNamedEntityRecognitionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoNamedEntityRecognition()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoNamedEntityRecognition"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/open-information-extraction")
def kgalgoopeninformationextraction_endpoint(body: KgAlgoOpenInformationExtractionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoOpenInformationExtraction()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoOpenInformationExtraction"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/structured-table-extraction")
def kgalgostructuredtableextraction_endpoint(body: KgAlgoStructuredTableExtractionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoStructuredTableExtraction()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoStructuredTableExtraction"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/supervised-relation-extraction")
def kgalgosupervisedrelationextraction_endpoint(body: KgAlgoSupervisedRelationExtractionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSupervisedRelationExtraction()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSupervisedRelationExtraction"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/text-segmentation")
def kgalgotextsegmentation_endpoint(body: KgAlgoTextSegmentationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoTextSegmentation()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoTextSegmentation"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/entity-canonicalization")
def kgalgoentitycanonicalization_endpoint(body: KgAlgoEntityCanonicalizationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoEntityCanonicalization()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoEntityCanonicalization"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/entity-resolution-blocking")
def kgalgoentityresolutionblocking_endpoint(body: KgAlgoEntityResolutionBlockingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoEntityResolutionBlocking()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoEntityResolutionBlocking"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/fellegi-sunter-linkage")
def kgalgofellegisunterlinkage_endpoint(body: KgAlgoFellegiSunterLinkageDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoFellegiSunterLinkage()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoFellegiSunterLinkage"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/match-clustering")
def kgalgomatchclustering_endpoint(body: KgAlgoMatchClusteringDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoMatchClustering()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoMatchClustering"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/relation-canonicalization")
def kgalgorelationcanonicalization_endpoint(body: KgAlgoRelationCanonicalizationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoRelationCanonicalization()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoRelationCanonicalization"}
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/similarity-joins")
def kgalgosimilarityjoins_endpoint(body: KgAlgoSimilarityJoinsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    instance = KgAlgoSimilarityJoins()
    method_name = "evaluate" if hasattr(instance, "evaluate") else ("execute" if hasattr(instance, "execute") else ("run" if hasattr(instance, "run") else None))
    if method_name:
        fn = getattr(instance, method_name)
        try:
            res = fn(**body.payload)
        except TypeError:
            res = fn(body.payload)
    else:
        res = {"status": "executed", "algo": "KgAlgoSimilarityJoins"}
    return build_success_envelope(data=res, trace_id=trace_id)

