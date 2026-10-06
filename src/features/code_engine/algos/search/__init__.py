"""
================================================================================
SEARCH ALGORITHMS PACKAGE (__init__.py)
================================================================================

Exposes all core pattern matching, regex engines, index structures, traversal
walkers, and re-exports categorized classifier & transform algorithms for
backward compatibility.
================================================================================
"""

# Walkers & Scanners
from src.features.code_engine.algos.search.search_algo_recursive_walk import SearchEngineRecursiveWalkAlgo
from src.features.code_engine.algos.search.search_algo_work_stealing_walker import SearchEngineWorkStealingWalkerAlgo
from src.features.code_engine.algos.search.search_algo_git_aware_walker import SearchEngineGitAwareWalkerAlgo
from src.features.code_engine.algos.search.search_algo_glob_matcher import SearchEngineGlobMatcherAlgo
from src.features.code_engine.algos.search.search_algo_trigram_index import SearchEngineTrigramIndexAlgo
from src.features.code_engine.algos.search.search_algo_simd_memchr import SearchEngineSimdMemchrAlgo
from src.features.code_engine.algos.search.search_algo_aho_corasick import SearchEngineAhoCorasickAlgo
from src.features.code_engine.algos.search.search_algo_lazy_dfa import SearchEngineLazyDfaAlgo
from src.features.code_engine.algos.search.search_algo_streaming_chunk_scanner import SearchEngineStreamingChunkScannerAlgo
from src.features.code_engine.algos.search.search_algo_context_snippet_collector import SearchEngineContextSnippetCollectorAlgo
from src.features.code_engine.algos.search.search_algo_mmap_scanner import SearchEngineMmapScannerAlgo

# Exact & Fuzzy String Matching
from src.features.code_engine.algos.search.search_algo_wu_manber import SearchEngineWuManberAlgo
from src.features.code_engine.algos.search.search_algo_z_algorithm import SearchEngineZAlgorithmAlgo
from src.features.code_engine.algos.search.search_algo_levenshtein_distance import SearchEngineLevenshteinDistanceAlgo
from src.features.code_engine.algos.search.search_algo_myers_bit_parallel import SearchEngineMyersBitParallelAlgo
from src.features.code_engine.algos.search.search_algo_levenshtein_automaton import SearchEngineLevenshteinAutomatonAlgo
from src.features.code_engine.algos.search.search_algo_bk_tree import SearchEngineBkTreeAlgo
from src.features.code_engine.algos.search.search_algo_minhash_jaccard import SearchEngineMinHashJaccardAlgo
from src.features.code_engine.algos.search.search_algo_fzf_fuzzy import SearchEngineFzfFuzzyAlgo

# Automata & Regular Expressions
from src.features.code_engine.algos.search.search_algo_regex_parser import SearchEngineRegexParserAlgo
from src.features.code_engine.algos.search.search_algo_thompson_nfa import SearchEngineThompsonNfaAlgo
from src.features.code_engine.algos.search.search_algo_pike_vm import SearchEnginePikeVmAlgo
from src.features.code_engine.algos.search.search_algo_backtracking_regex import SearchEngineBacktrackingRegexAlgo
from src.features.code_engine.algos.search.search_algo_subset_dfa import SearchEngineSubsetDfaAlgo
from src.features.code_engine.algos.search.search_algo_lazy_hybrid_dfa import SearchEngineLazyHybridDfaAlgo
from src.features.code_engine.algos.search.search_algo_hyperscan_regex_set import SearchEngineHyperscanRegexSetAlgo
from src.features.code_engine.algos.search.search_algo_redos_protection import SearchEngineReDosProtectionAlgo

# Inverted Indexes & Suffix Structures
from src.features.code_engine.algos.search.search_algo_inverted_index import SearchEngineInvertedIndexAlgo
from src.features.code_engine.algos.search.search_algo_trigram_inverted_index import SearchEngineTrigramInvertedIndexAlgo
from src.features.code_engine.algos.search.search_algo_positional_trigram_index import SearchEnginePositionalTrigramIndexAlgo
from src.features.code_engine.algos.search.search_algo_sparse_ngrams import SearchEngineSparseNgramsAlgo
from src.features.code_engine.algos.search.search_algo_suffix_array_sais import SearchEngineSuffixArraySaisAlgo
from src.features.code_engine.algos.search.search_algo_suffix_automaton import SearchEngineSuffixAutomatonAlgo
from src.features.code_engine.algos.search.search_algo_fm_index import SearchEngineFmIndexAlgo
from src.features.code_engine.algos.search.search_algo_trie import SearchEngineTrieAlgo
from src.features.code_engine.algos.search.search_algo_radix_tree import SearchEngineRadixTreeAlgo
from src.features.code_engine.algos.search.search_algo_fst import SearchEngineFstAlgo
from src.features.code_engine.algos.search.search_algo_b_plus_tree import SearchEngineBPlusTreeAlgo
from src.features.code_engine.algos.search.search_algo_lsm_tree import SearchEngineLsmTreeAlgo
from src.features.code_engine.algos.search.search_algo_bloom_filter import SearchEngineBloomFilterAlgo
from src.features.code_engine.algos.search.search_algo_xor_filter import SearchEngineXorFilterAlgo
from src.features.code_engine.algos.search.search_algo_posting_list import SearchEnginePostingListAlgo
from src.features.code_engine.algos.search.search_algo_roaring_bitmap import SearchEngineRoaringBitmapAlgo

# Query Execution & Postings Intersection
from src.features.code_engine.algos.search.search_algo_merge_intersection import SearchEngineMergeIntersectionAlgo
from src.features.code_engine.algos.search.search_algo_galloping_intersection import SearchEngineGallopingIntersectionAlgo
from src.features.code_engine.algos.search.search_algo_k_way_merge_heap import SearchEngineKWayMergeHeapAlgo
from src.features.code_engine.algos.search.search_algo_block_max_wand import SearchEngineBlockMaxWandAlgo
from src.features.code_engine.algos.search.search_algo_rarest_first_ordering import SearchEngineRarestFirstOrderingAlgo
from src.features.code_engine.algos.search.search_algo_candidate_verification import SearchEngineCandidateVerificationAlgo
from src.features.code_engine.algos.search.search_algo_early_termination import SearchEngineEarlyTerminationAlgo
from src.features.code_engine.algos.search.search_algo_scatter_gather import SearchEngineScatterGatherAlgo
from src.features.code_engine.algos.search.search_algo_hedged_requests import SearchEngineHedgedRequestsAlgo
from src.features.code_engine.algos.search.search_algo_index_versioned_cache import SearchEngineIndexVersionedCacheAlgo

# AST & Structural Search
from src.features.code_engine.algos.search.search_algo_tokenizer_search import SearchEngineTokenizerSearchAlgo
from src.features.code_engine.algos.search.search_algo_concrete_syntax_tree import SearchEngineConcreteSyntaxTreeAlgo
from src.features.code_engine.algos.search.search_algo_abstract_syntax_tree import SearchEngineAbstractSyntaxTreeAlgo
from src.features.code_engine.algos.search.search_algo_incremental_parser import SearchEngineIncrementalParserAlgo
from src.features.code_engine.algos.search.search_algo_tree_sitter_query import SearchEngineTreeSitterQueryAlgo
from src.features.code_engine.algos.search.search_algo_ast_grep_pattern import SearchEngineAstGrepPatternAlgo
from src.features.code_engine.algos.search.search_algo_semgrep_equivalence import SearchEngineSemgrepEquivalenceAlgo
from src.features.code_engine.algos.search.search_algo_comby_delimiter import SearchEngineCombyDelimiterAlgo
from src.features.code_engine.algos.search.search_algo_subtree_hash_clone import SearchEngineSubtreeHashCloneAlgo
from src.features.code_engine.algos.search.search_algo_gum_tree_diff import SearchEngineGumTreeDiffAlgo
from src.features.code_engine.algos.search.search_algo_symbol_table import SearchEngineSymbolTableAlgo
from src.features.code_engine.algos.search.search_algo_scope_graph import SearchEngineScopeGraphAlgo
from src.features.code_engine.algos.search.search_algo_stack_graph import SearchEngineStackGraphAlgo
from src.features.code_engine.algos.search.search_algo_lsp_protocol import SearchEngineLspProtocolAlgo
from src.features.code_engine.algos.search.search_algo_scip_lsif_index import SearchEngineScipLsifIndexAlgo
from src.features.code_engine.algos.search.search_algo_call_graph import SearchEngineCallGraphAlgo
from src.features.code_engine.algos.search.search_algo_import_dependency_graph import SearchEngineImportDependencyGraphAlgo
from src.features.code_engine.algos.search.search_algo_control_flow_graph import SearchEngineControlFlowGraphAlgo
from src.features.code_engine.algos.search.search_algo_ssa_form import SearchEngineSsaFormAlgo
from src.features.code_engine.algos.search.search_algo_dataflow_worklist import SearchEngineDataflowWorklistAlgo
from src.features.code_engine.algos.search.search_algo_taint_analysis import SearchEngineTaintAnalysisAlgo
from src.features.code_engine.algos.search.search_algo_datalog_codeql import SearchEngineDatalogCodeqlAlgo
from src.features.code_engine.algos.search.search_algo_code_embeddings import SearchEngineCodeEmbeddingsAlgo

# Re-exports from classifier package for backwards compatibility
from src.features.code_engine.algos.classifier import (
    ClassifierAlgoBinaryClassifier,
    SearchEngineBinaryClassifierAlgo,
    ClassifierAlgoGeneratedCode,
    SearchEngineGeneratedCodeClassifierAlgo,
    ClassifierAlgoContentTypeProber,
    SearchEngineContentTypeProberAlgo,
    ClassifierAlgoSizeLineBouncer,
    SearchEngineSizeLineBouncerAlgo,
)

# Re-exports from transform package for backwards compatibility
from src.features.code_engine.algos.transform import (
    TransformAlgoBurrowsWheeler,
    SearchEngineBurrowsWheelerTransformAlgo,
    TransformAlgoDeltaGapEncoding,
    SearchEngineDeltaGapEncodingAlgo,
    TransformAlgoVarintEncoding,
    SearchEngineVarintEncodingAlgo,
    TransformAlgoBitPackingPforDelta,
    SearchEngineBitPackingPforDeltaAlgo,
    TransformAlgoEliasFano,
    SearchEngineEliasFanoAlgo,
    TransformAlgoLcpArrayKasai,
    SearchEngineLcpArrayKasaiAlgo,
    TransformAlgoAstChunking,
    SearchEngineAstChunkingAlgo,
    TransformAlgoBooleanQuerySimplifier,
    SearchEngineBooleanQuerySimplifierAlgo,
    TransformAlgoReverseInnerOptimizer,
    SearchEngineReverseInnerOptimizerAlgo,
    TransformAlgoRegexToTrigramQuery,
    SearchEngineRegexToTrigramQueryAlgo,
    TransformAlgoLiteralExtraction,
    SearchEngineLiteralExtractionAlgo,
)

__all__ = [
    # Walkers & Scanners
    "SearchEngineRecursiveWalkAlgo",
    "SearchEngineWorkStealingWalkerAlgo",
    "SearchEngineGitAwareWalkerAlgo",
    "SearchEngineGlobMatcherAlgo",
    "SearchEngineTrigramIndexAlgo",
    "SearchEngineSimdMemchrAlgo",
    "SearchEngineAhoCorasickAlgo",
    "SearchEngineLazyDfaAlgo",
    "SearchEngineStreamingChunkScannerAlgo",
    "SearchEngineContextSnippetCollectorAlgo",
    "SearchEngineMmapScannerAlgo",
    # Matching
    "SearchEngineWuManberAlgo",
    "SearchEngineZAlgorithmAlgo",
    "SearchEngineLevenshteinDistanceAlgo",
    "SearchEngineMyersBitParallelAlgo",
    "SearchEngineLevenshteinAutomatonAlgo",
    "SearchEngineBkTreeAlgo",
    "SearchEngineMinHashJaccardAlgo",
    "SearchEngineFzfFuzzyAlgo",
    # Automata
    "SearchEngineRegexParserAlgo",
    "SearchEngineThompsonNfaAlgo",
    "SearchEnginePikeVmAlgo",
    "SearchEngineBacktrackingRegexAlgo",
    "SearchEngineSubsetDfaAlgo",
    "SearchEngineLazyHybridDfaAlgo",
    "SearchEngineHyperscanRegexSetAlgo",
    "SearchEngineReDosProtectionAlgo",
    # Indexes
    "SearchEngineInvertedIndexAlgo",
    "SearchEngineTrigramInvertedIndexAlgo",
    "SearchEnginePositionalTrigramIndexAlgo",
    "SearchEngineSparseNgramsAlgo",
    "SearchEngineSuffixArraySaisAlgo",
    "SearchEngineSuffixAutomatonAlgo",
    "SearchEngineFmIndexAlgo",
    "SearchEngineTrieAlgo",
    "SearchEngineRadixTreeAlgo",
    "SearchEngineFstAlgo",
    "SearchEngineBPlusTreeAlgo",
    "SearchEngineLsmTreeAlgo",
    "SearchEngineBloomFilterAlgo",
    "SearchEngineXorFilterAlgo",
    "SearchEnginePostingListAlgo",
    "SearchEngineRoaringBitmapAlgo",
    # Intersect & Query
    "SearchEngineMergeIntersectionAlgo",
    "SearchEngineGallopingIntersectionAlgo",
    "SearchEngineKWayMergeHeapAlgo",
    "SearchEngineBlockMaxWandAlgo",
    "SearchEngineRarestFirstOrderingAlgo",
    "SearchEngineCandidateVerificationAlgo",
    "SearchEngineEarlyTerminationAlgo",
    "SearchEngineScatterGatherAlgo",
    "SearchEngineHedgedRequestsAlgo",
    "SearchEngineIndexVersionedCacheAlgo",
    # Structural
    "SearchEngineTokenizerSearchAlgo",
    "SearchEngineConcreteSyntaxTreeAlgo",
    "SearchEngineAbstractSyntaxTreeAlgo",
    "SearchEngineIncrementalParserAlgo",
    "SearchEngineTreeSitterQueryAlgo",
    "SearchEngineAstGrepPatternAlgo",
    "SearchEngineSemgrepEquivalenceAlgo",
    "SearchEngineCombyDelimiterAlgo",
    "SearchEngineSubtreeHashCloneAlgo",
    "SearchEngineGumTreeDiffAlgo",
    "SearchEngineSymbolTableAlgo",
    "SearchEngineScopeGraphAlgo",
    "SearchEngineStackGraphAlgo",
    "SearchEngineLspProtocolAlgo",
    "SearchEngineScipLsifIndexAlgo",
    "SearchEngineCallGraphAlgo",
    "SearchEngineImportDependencyGraphAlgo",
    "SearchEngineControlFlowGraphAlgo",
    "SearchEngineSsaFormAlgo",
    "SearchEngineDataflowWorklistAlgo",
    "SearchEngineTaintAnalysisAlgo",
    "SearchEngineDatalogCodeqlAlgo",
    "SearchEngineCodeEmbeddingsAlgo",
    # Classifiers (re-exported)
    "ClassifierAlgoBinaryClassifier",
    "SearchEngineBinaryClassifierAlgo",
    "ClassifierAlgoGeneratedCode",
    "SearchEngineGeneratedCodeClassifierAlgo",
    "ClassifierAlgoContentTypeProber",
    "SearchEngineContentTypeProberAlgo",
    "ClassifierAlgoSizeLineBouncer",
    "SearchEngineSizeLineBouncerAlgo",
    # Transforms (re-exported)
    "TransformAlgoBurrowsWheeler",
    "SearchEngineBurrowsWheelerTransformAlgo",
    "TransformAlgoDeltaGapEncoding",
    "SearchEngineDeltaGapEncodingAlgo",
    "TransformAlgoVarintEncoding",
    "SearchEngineVarintEncodingAlgo",
    "TransformAlgoBitPackingPforDelta",
    "SearchEngineBitPackingPforDeltaAlgo",
    "TransformAlgoEliasFano",
    "SearchEngineEliasFanoAlgo",
    "TransformAlgoLcpArrayKasai",
    "SearchEngineLcpArrayKasaiAlgo",
    "TransformAlgoAstChunking",
    "SearchEngineAstChunkingAlgo",
    "TransformAlgoBooleanQuerySimplifier",
    "SearchEngineBooleanQuerySimplifierAlgo",
    "TransformAlgoReverseInnerOptimizer",
    "SearchEngineReverseInnerOptimizerAlgo",
    "TransformAlgoRegexToTrigramQuery",
    "SearchEngineRegexToTrigramQueryAlgo",
    "TransformAlgoLiteralExtraction",
    "SearchEngineLiteralExtractionAlgo",
]
