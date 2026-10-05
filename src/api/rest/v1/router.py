"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 UNIFIED FACADE ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Unified facade aggregator composing all modular role-based routers for REST API V1:
   - System & Domain Router (System health, RAG, AI agents, audit, graph, catalog)
   - Search Algorithms Router (ALGO-SRCH-01..15)
   - Observability Algorithms Router (ALGO-OBS-16..21)
   - Update Algorithms Router (ALGO-UPD-22..24)
   - Base Vector Algorithms Router (ALGO-VEC-01..09)
   - Graph Algorithms Router (ALGO-GRAPH-01..09)
   - Vector Filter Algorithms Router (ALGO-VEC-FLTR-80..84)
   - Vector Search Algorithms Router (ALGO-VEC-SRCH-51..110)
   - Vector Transform Algorithms Router (ALGO-VEC-TRFM-01..50)

2. ZERO-INLINE-COMMENT DOCTRINE & COMPLIANCE:
   Decomposes the monolithic router into modular role-specific sub-routers while
   maintaining 100% backward compatibility, preserving all public DTOs, endpoint
   handlers, and dependency injection factories.
================================================================================
"""

from fastapi import APIRouter
from src.api.rest.v1.dependencies import get_services, get_code_engine_service, get_orchestrator_services

router = APIRouter(prefix="/api/v1")

from src.api.rest.v1.routers.system_router import router as system_router
router.include_router(system_router)

from src.api.rest.v1.routers.search_router import router as search_router
router.include_router(search_router)

from src.api.rest.v1.routers.observability_router import router as observability_router
router.include_router(observability_router)

from src.api.rest.v1.routers.update_router import router as update_router
router.include_router(update_router)

from src.api.rest.v1.routers.vector_router import router as vector_router
router.include_router(vector_router)

from src.api.rest.v1.routers.graph_router import router as graph_router
router.include_router(graph_router)

from src.api.rest.v1.routers.vector_filter_router import router as vector_filter_router
router.include_router(vector_filter_router)

from src.api.rest.v1.routers.vector_search_router import router as vector_search_router
router.include_router(vector_search_router)

from src.api.rest.v1.routers.vector_transform_router import router as vector_transform_router
router.include_router(vector_transform_router)

# -----------------------------------------------------------------------------
# RE-EXPORTS FOR FULL BACKWARD COMPATIBILITY
# -----------------------------------------------------------------------------

from src.api.rest.v1.routers.system_router import (
    GraphQueryDTO,
    AlgoComposeRequestDTO,
    AlgoExecuteRequestDTO,
    health_check,
    index_policies,
    search_policies,
    run_agent,
    list_declarative_agents,
    run_specialized_agent,
    scan_repository,
    execute_algorithm_direct,
    build_graph,
    query_graph,
    get_rule_impact,
    list_algorithm_contracts,
    get_algorithm_contract,
    list_type_adapters,
    compose_algorithm_pipeline,
)

from src.api.rest.v1.routers.search_router import (
    AlgoScanDTO,
    FilePathDTO,
    DirectoryPathDTO,
    SearchWalkDTO,
    SearchWorkStealingDTO,
    SearchGitAwareDTO,
    SearchGlobDTO,
    SearchSizeLineDTO,
    SearchTrigramDTO,
    SearchSimdMemchrDTO,
    SearchAhoCorasickDTO,
    SearchLazyDfaDTO,
    SearchContextSnippetDTO,
    SearchMmapDTO,
    search_recursive_walk,
    search_work_stealing_walk,
    search_git_aware_walk,
    search_glob_match,
    search_binary_check,
    search_content_type,
    search_size_line_check,
    search_generated_code_check,
    search_trigram_index,
    search_simd_memchr,
    search_aho_corasick,
    search_lazy_dfa,
    search_streaming_chunk_scan,
    search_context_snippet,
    search_mmap_scan,
    scan_multipattern,
)

from src.api.rest.v1.routers.observability_router import (
    ObsSpanTrackDTO,
    ObsAstDTO,
    ObsSymbolsDTO,
    obs_span_track,
    obs_ast_extract,
    obs_symbols_resolve,
    lint_comments,
    analyze_dependencies,
    generate_file_outline,
)

from src.api.rest.v1.routers.update_router import (
    PatchOperationDTO,
    BatchPatchRequestDTO,
    DiffRequestDTO,
    UpdateCstMatchDTO,
    update_cst_match,
    apply_patch,
    generate_diff,
)

from src.api.rest.v1.routers.vector_router import (
    VectorNormalizeDTO,
    VectorCenterDTO,
    VectorLayerNormDTO,
    VectorScaleDTO,
    VectorSliceDTO,
    VectorScalarQuantizeDTO,
    VectorBinaryQuantizeDTO,
    VectorPoolDTO,
    VectorChunkDTO,
    normalize_vector_endpoint,
    center_vectors_endpoint,
    layer_norm_endpoint,
    scale_vector_endpoint,
    slice_vector_endpoint,
    quantize_scalar_endpoint,
    quantize_binary_endpoint,
    pool_tokens_endpoint,
    chunk_text_endpoint,
)

from src.api.rest.v1.routers.graph_router import (
    GraphBfsDTO,
    GraphDfsDTO,
    GraphDijkstraDTO,
    GraphAstarDTO,
    GraphPageRankDTO,
    GraphDegreeCentralityDTO,
    GraphConnectedComponentsDTO,
    GraphTarjanSccDTO,
    GraphSubgraphMatchDTO,
    graph_bfs_endpoint,
    graph_dfs_endpoint,
    graph_dijkstra_endpoint,
    graph_astar_endpoint,
    graph_pagerank_endpoint,
    graph_degree_centrality_endpoint,
    graph_connected_components_endpoint,
    graph_tarjan_scc_endpoint,
    graph_subgraph_match_endpoint,
)

from src.api.rest.v1.routers.vector_filter_router import (
    VecFilterPreFilterDTO,
    VecFilterPostFilterDTO,
    VecFilterInGraphDTO,
    VecFilterSelectivityPlanDTO,
    VecFilterPartitionedDTO,
    vector_filter_pre_filter_endpoint,
    vector_filter_post_filter_endpoint,
    vector_filter_in_graph_endpoint,
    vector_filter_selectivity_plan_endpoint,
    vector_filter_partitioned_endpoint,
)

from src.api.rest.v1.routers.vector_search_router import (
    VecSearchBruteForceGemmDTO,
    VecSearchSimdDistanceDTO,
    VecSearchHeapTopKDTO,
    VecSearchRadixTopKDTO,
    VecSearchEarlyAbandonDTO,
    VecSearchPivotPruneDTO,
    VecSearchKdTreeDTO,
    VecSearchBallTreeDTO,
    VecSearchVpTreeDTO,
    VecSearchRpForestDTO,
    VecSearchIvfDTO,
    VecSearchIvfPqDTO,
    VecSearchNprobeTunerDTO,
    VecSearchInvertedMultiIndexDTO,
    VecSearchNswDTO,
    VecSearchHnswSearchDTO,
    VecSearchHnswInsertDTO,
    VecSearchBeamSearchDTO,
    VecSearchVamanaDTO,
    VecSearchRobustPruneDTO,
    VecSearchNsgDTO,
    VecSearchCagraDTO,
    VecSearchEntryPointDTO,
    VecSearchConnectivityRepairDTO,
    VecSearchFilteredDiskannDTO,
    VecSearchSpannDTO,
    VecSearchRandomHyperplaneLshDTO,
    VecSearchMultiProbeLshDTO,
    VecSearchE2LshDTO,
    VecSearchBM25DTO,
    VecSearchSparseDenseHybridDTO,
    VecSearchRRFDTO,
    VecSearchConvexScoreFusionDTO,
    VecSearchMMRDTO,
    VecSearchRangeSearchDTO,
    VecSearchMaxSimDTO,
    VecSearchMultiQueryExpansionDTO,
    VecSearchFullPrecisionRescoreDTO,
    VecSearchCrossEncoderRerankDTO,
    VecSearchMultiStageFunnelDTO,
    VecSearchLLMListwiseRerankDTO,
    VecSearchHyDEDTO,
    VecSearchQueryRoutingDTO,
    VecSearchScatterGatherDTO,
    VecSearchPartitionAwareRoutingDTO,
    VecSearchReplicationLoadBalancerDTO,
    VecSearchHedgedRequestsDTO,
    VecSearchKWayMergeDTO,
    VecSearchQueryCacheDTO,
    VecSearchSemanticCacheDTO,
    VecSearchQueryBatchingDTO,
    VecSearchMemoryTieringDTO,
    VecSearchDiskIOSchedulerDTO,
    VecSearchAdmissionControlDTO,
    VecSearchSearchAutotuneDTO,
    vector_search_gemm_endpoint,
    vector_search_simd_dist_endpoint,
    vector_search_topk_endpoint,
    vector_search_radix_topk_endpoint,
    vector_search_early_abandon_endpoint,
    vector_search_pivot_prune_endpoint,
    vector_search_kdtree_endpoint,
    vector_search_ball_tree_endpoint,
    vector_search_vptree_endpoint,
    vector_search_rp_forest_endpoint,
    vector_search_ivf_endpoint,
    vector_search_ivf_pq_endpoint,
    vector_search_nprobe_tune_endpoint,
    vector_search_imi_endpoint,
    vector_search_nsw_endpoint,
    vector_search_hnsw_search_endpoint,
    vector_search_hnsw_insert_endpoint,
    vector_search_beam_search_endpoint,
    vector_search_vamana_endpoint,
    vector_search_robust_prune_endpoint,
    vector_search_nsg_endpoint,
    vector_search_cagra_endpoint,
    vector_search_entry_point_endpoint,
    vector_search_connectivity_repair_endpoint,
    vector_search_filtered_diskann_endpoint,
    vector_search_spann_endpoint,
    vector_search_random_hyperplane_lsh_endpoint,
    vector_search_multi_probe_lsh_endpoint,
    vector_search_e2lsh_endpoint,
    vector_search_bm25_endpoint,
    vector_search_sparse_dense_hybrid_endpoint,
    vector_search_rrf_endpoint,
    vector_search_convex_score_fusion_endpoint,
    vector_search_mmr_endpoint,
    vector_search_range_search_endpoint,
    vector_search_maxsim_endpoint,
    vector_search_multi_query_expansion_endpoint,
    vector_search_full_precision_rescore_endpoint,
    vector_search_cross_encoder_rerank_endpoint,
    vector_search_multi_stage_funnel_endpoint,
    vector_search_llm_listwise_rerank_endpoint,
    vector_search_hyde_endpoint,
    vector_search_query_routing_endpoint,
    vector_search_scatter_gather_endpoint,
    vector_search_partition_aware_routing_endpoint,
    vector_search_replication_load_balancer_endpoint,
    vector_search_hedged_requests_endpoint,
    vector_search_kway_merge_endpoint,
    vector_search_query_cache_endpoint,
    vector_search_semantic_cache_endpoint,
    vector_search_query_batching_endpoint,
    vector_search_memory_tiering_endpoint,
    vector_search_disk_io_scheduler_endpoint,
    vector_search_admission_control_endpoint,
    vector_search_search_autotune_endpoint,
)

from src.api.rest.v1.routers.vector_transform_router import (
    VecTransformSubwordTokenizationDTO,
    VecTransformBiEncoderForwardDTO,
    VecTransformMeanPoolingDTO,
    VecTransformCLSPoolingDTO,
    VecTransformLastTokenPoolingDTO,
    VecTransformInstructionPrefixesDTO,
    VecTransformContrastiveInfoNCEDTO,
    VecTransformHardNegativeMiningDTO,
    VecTransformMatryoshkaLearningDTO,
    VecTransformLateChunkingDTO,
    VecTransformSlidingWindowDTO,
    VecTransformSemanticChunkingDTO,
    VecTransformRecursiveChunkingDTO,
    VecTransformDynamicPaddingBatchingDTO,
    VecTransformL2NormDTO,
    VecTransformMeanCenteringDTO,
    VecTransformWhiteningDTO,
    VecTransformRemoveDominantDirectionsDTO,
    VecTransformMIPSToNNSDTO,
    VecTransformScoreCalibrationDTO,
    VecTransformCSLSHubnessReductionDTO,
    VecTransformProcrustesAlignmentDTO,
    VecTransformPCADTO,
    VecTransformTruncatedSVDDTO,
    VecTransformRandomProjectionDTO,
    VecTransformAutoencoderCompressionDTO,
    VecTransformUMAPDTO,
    VecTransformTSNEDTO,
    VecTransformProjectionHeadDTO,
    VecTransformIncrementalPCADTO,
    VecTransformSimHashDTO,
    VecTransformLearnedSparseExpansionDTO,
    VecTransformScalarQuantizationDTO,
    VecTransformBinaryQuantizationDTO,
    VecTransformProductQuantizationDTO,
    VecTransformOptimizedProductQuantizationDTO,
    VecTransformResidualQuantizationDTO,
    VecTransformAnisotropicQuantizationDTO,
    VecTransformKMeansClusteringDTO,
    VecTransformKMeansPlusPlusDTO,
    VecTransformMinibatchKMeansDTO,
    VecTransformHierarchicalKMeansDTO,
    VecTransformADCLookupDTO,
    VecTransformFastScanPQDTO,
    VecTransformRaBiTQDTO,
    VecTransformHalfPrecisionDTO,
    VecTransformMultiVectorRepresentationDTO,
    VecTransformMultiVectorCompressionDTO,
    VecTransformSparseVectorRepresentationDTO,
    VecTransformEmbeddingCacheDTO,
    vector_transform_subword_tokenization_endpoint,
    vector_transform_bi_encoder_forward_endpoint,
    vector_transform_mean_pooling_endpoint,
    vector_transform_cls_pooling_endpoint,
    vector_transform_last_token_pooling_endpoint,
    vector_transform_instruction_prefixes_endpoint,
    vector_transform_contrastive_infonce_endpoint,
    vector_transform_hard_negative_mining_endpoint,
    vector_transform_matryoshka_learning_endpoint,
    vector_transform_late_chunking_endpoint,
    vector_transform_sliding_window_endpoint,
    vector_transform_semantic_chunking_endpoint,
    vector_transform_recursive_chunking_endpoint,
    vector_transform_dynamic_padding_batching_endpoint,
    vector_transform_l2_norm_endpoint,
    vector_transform_mean_centering_endpoint,
    vector_transform_whitening_endpoint,
    vector_transform_remove_dominant_directions_endpoint,
    vector_transform_mips_to_nns_endpoint,
    vector_transform_score_calibration_endpoint,
    vector_transform_csls_hubness_reduction_endpoint,
    vector_transform_procrustes_alignment_endpoint,
    vector_transform_pca_endpoint,
    vector_transform_truncated_svd_endpoint,
    vector_transform_random_projection_endpoint,
    vector_transform_autoencoder_compression_endpoint,
    vector_transform_umap_endpoint,
    vector_transform_tsne_endpoint,
    vector_transform_projection_head_endpoint,
    vector_transform_incremental_pca_endpoint,
    vector_transform_simhash_endpoint,
    vector_transform_learned_sparse_expansion_endpoint,
    vector_transform_scalar_quantization_endpoint,
    vector_transform_binary_quantization_endpoint,
    vector_transform_product_quantization_endpoint,
    vector_transform_optimized_product_quantization_endpoint,
    vector_transform_residual_quantization_endpoint,
    vector_transform_anisotropic_quantization_endpoint,
    vector_transform_kmeans_clustering_endpoint,
    vector_transform_kmeans_plus_plus_endpoint,
    vector_transform_minibatch_kmeans_endpoint,
    vector_transform_hierarchical_kmeans_endpoint,
    vector_transform_adc_lookup_endpoint,
    vector_transform_fast_scan_pq_endpoint,
    vector_transform_rabitq_endpoint,
    vector_transform_half_precision_endpoint,
    vector_transform_multi_vector_representation_endpoint,
    vector_transform_multi_vector_compression_endpoint,
    vector_transform_sparse_vector_representation_endpoint,
    vector_transform_embedding_cache_endpoint,
)
