"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 SEARCH ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the Layer 1 Search Algorithms Suite
   (ALGO-SRCH-01 through ALGO-SRCH-100):
   - Fast file tree discovery (walk, work-stealing, git-aware, glob, binary check)
   - Pattern matching & multi-string (trigram, memchr, aho-corasick, lazy-dfa, wu-manber)
   - Approximate & fuzzy matching (levenshtein, myers, automaton, bk-tree, minhash, fzf)
   - Regex engines & parsing (regex-parser, thompson-nfa, pike-vm, backtracking, subset-dfa)
   - Regex optimizations (lazy-dfa, literal-extraction, reverse-optimizer, hyperscan, redos)
   - Index structures (inverted-index, trigram-index, positional-trigram, sparse-ngrams)
   - Suffix structures & transforms (suffix-array, lcp-array, suffix-automaton, bwt)
   - Compact Indexes & Filters (fm-index, trie, radix-tree, fst, b-plus-tree, lsm-tree, bloom, xor)
   - Inverted Index Compression (posting-list, delta-gap, varint, pfor-delta, elias-fano, roaring)
   - Query Evaluation & Pruning (merge, galloping, k-way heap, block-max wand, regex-to-trigram, bqs, rarest-first, candidate-verify, early-term)
   - Distributed & Resilient Search (scatter-gather, hedged-requests, versioned-cache)
   - Syntax & Structural Parsing (tokenizer, cst, ast, incremental-parser, tree-sitter, ast-grep, semgrep, comby, clone, gumtree)
   - Symbol & Semantic Resolution (symbol-table, scope-graph, stack-graph, lsp, scip-lsif)
   - Program Analysis & Representations (call-graph, import-dep-graph, cfg, ssa, dataflow, taint, datalog-codeql)
   - Code-Specific Search (ast-chunking, code-embeddings)

2. ZERO-INLINE-COMMENT DOCTRINE:
   No inline comments inside functions; all contracts and schemas documented in docblock.
================================================================================
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from ..dependencies import get_code_engine_service

router = APIRouter()

class AlgoScanDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to scan")
    patterns: List[str] = Field(..., description="Patterns to search for")
    max_files: int = Field(default=1000, description="Max files to scan")


class FilePathDTO(BaseModel):
    file_path: str = Field(..., description="File path to analyze")


class DirectoryPathDTO(BaseModel):
    directory: str = Field(default=".", description="Directory path to analyze")

class SearchWalkDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to walk")
    max_depth: Optional[int] = Field(default=None, description="Maximum directory traversal depth")
    allowed_extensions: Optional[List[str]] = Field(default=None, description="Allowed file extensions")


class SearchWorkStealingDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to walk")
    workers: int = Field(default=4, description="Parallel worker threads")


class SearchGitAwareDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to walk")
    ignore_files: Optional[List[str]] = Field(default=None, description="Custom ignore patterns")


class SearchGlobDTO(BaseModel):
    pattern: str = Field(..., description="Glob pattern")
    path: str = Field(..., description="File path to test")


class SearchSizeLineDTO(BaseModel):
    file_path: str = Field(..., description="Target file path")
    max_bytes: int = Field(default=10485760, description="Max allowed bytes")
    max_lines: int = Field(default=50000, description="Max allowed lines")


class SearchTrigramDTO(BaseModel):
    text: str = Field(..., description="Input text to index into trigrams")


class SearchSimdMemchrDTO(BaseModel):
    data: str = Field(..., description="Input text/data")
    byte: str = Field(default="\n", description="Target character/byte to search")


class SearchAhoCorasickDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    patterns: List[str] = Field(..., description="Needle patterns to match simultaneously")


class SearchLazyDfaDTO(BaseModel):
    pattern: str = Field(..., description="Regex pattern")
    text: str = Field(..., description="Text to match against")


class SearchContextSnippetDTO(BaseModel):
    lines: List[str] = Field(..., description="File lines")
    line_number: int = Field(..., description="1-based match line number")
    lines_before: int = Field(default=2, description="Leading context lines")
    lines_after: int = Field(default=2, description="Trailing context lines")


class SearchMmapDTO(BaseModel):
    file_path: str = Field(..., description="Path to file")
    pattern: str = Field(..., description="Byte/text pattern to find")


class SearchWuManberDTO(BaseModel):
    text: str = Field(..., description="Haystack text to scan")
    patterns: List[str] = Field(..., description="Keywords to search simultaneously")
    block_size: int = Field(default=2, description="B-gram block size")


class SearchZAlgorithmDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Needle pattern")
    delimiter: str = Field(default="$", description="Unique delimiter character")


class SearchLevenshteinDistanceDTO(BaseModel):
    source: str = Field(..., description="Source string")
    target: str = Field(..., description="Target string")
    insert_cost: int = Field(default=1, description="Insertion cost")
    delete_cost: int = Field(default=1, description="Deletion cost")
    substitute_cost: int = Field(default=1, description="Substitution cost")
    include_matrix: bool = Field(default=False, description="Whether to include full DP matrix")


class SearchMyersBitParallelDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Needle pattern (up to 64 chars)")
    max_distance: int = Field(default=2, description="Maximum edit distance threshold")


class SearchLevenshteinAutomatonDTO(BaseModel):
    pattern: str = Field(..., description="Base target pattern")
    candidates: List[str] = Field(..., description="Candidate strings to filter")
    max_distance: int = Field(default=2, description="Maximum Levenshtein distance radius")


class SearchBkTreeDTO(BaseModel):
    dictionary: List[str] = Field(..., description="Word dictionary to index")
    query: str = Field(..., description="Query word to search")
    max_distance: int = Field(default=2, description="Search distance radius")


class SearchMinHashJaccardDTO(BaseModel):
    documents: List[Dict[str, str]] = Field(..., description="List of documents with id and text")
    num_perm: int = Field(default=64, description="Number of hash permutations")
    shingle_size: int = Field(default=3, description="Token shingle size")
    bands: int = Field(default=16, description="LSH bands")
    similarity_threshold: float = Field(default=0.5, description="Minimum Jaccard similarity")


class SearchFzfFuzzyDTO(BaseModel):
    candidates: List[str] = Field(..., description="Candidate paths or symbols")
    query: str = Field(..., description="Fuzzy query string")
    case_sensitive: bool = Field(default=False, description="Case sensitivity flag")


class SearchRegexParserDTO(BaseModel):
    pattern: str = Field(..., description="Regular expression pattern to parse into AST")


class SearchThompsonNfaDTO(BaseModel):
    pattern: str = Field(..., description="Regular expression pattern to compile to NFA")


class SearchPikeVmDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Regular expression pattern")


class SearchBacktrackingRegexDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Pattern supporting lookarounds and backrefs")
    max_steps: int = Field(default=50000, description="Step execution budget cap")


class SearchSubsetDfaDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Regular expression pattern")


class SearchLazyHybridDfaDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Regular expression pattern")
    max_cached_states: int = Field(default=1000, description="Maximum cached DFA state transitions")


class SearchLiteralExtractionDTO(BaseModel):
    pattern: str = Field(..., description="Regular expression pattern to analyze")
    min_literal_length: int = Field(default=2, description="Minimum length for extracted literals")


class SearchReverseInnerOptimizerDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    pattern: str = Field(..., description="Regular expression pattern")
    max_lookback: int = Field(default=128, description="Maximum lookback window in bytes")


class SearchHyperscanRegexSetDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    rules: List[Dict[str, str]] = Field(..., description="List of rule objects with id and pattern")


class SearchReDosProtectionDTO(BaseModel):
    pattern: str = Field(..., description="Regular expression pattern to statically analyze")


class SearchInvertedIndexDTO(BaseModel):
    documents: List[Dict[str, str]] = Field(..., description="List of documents with id and text")
    query_terms: List[str] = Field(..., description="Search terms to resolve")
    operation: str = Field(default="AND", description="Boolean operation (AND or OR)")


class SearchTrigramInvertedIndexDTO(BaseModel):
    documents: List[Dict[str, str]] = Field(..., description="List of documents with id and text")
    query: str = Field(..., description="Substring query")


class SearchPositionalTrigramIndexDTO(BaseModel):
    documents: List[Dict[str, str]] = Field(..., description="List of documents with id and text")
    query: str = Field(..., description="Substring query")


class SearchSparseNgramsDTO(BaseModel):
    text: str = Field(..., description="Input text to extract variable-length sparse n-grams from")
    min_gram_len: int = Field(default=3, description="Minimum gram length")
    max_gram_len: int = Field(default=8, description="Maximum gram length")


class SearchSuffixArraySaisDTO(BaseModel):
    text: str = Field(..., description="Haystack text to index")
    pattern: str = Field(..., description="Substring query pattern")


class SearchLcpArrayKasaiDTO(BaseModel):
    text: str = Field(..., description="Input text to compute Longest Common Prefix array")


class SearchSuffixAutomatonDTO(BaseModel):
    text: str = Field(..., description="Haystack text to index into DAWG")
    query: str = Field(..., description="Substring query to verify")


class SearchBurrowsWheelerTransformDTO(BaseModel):
    text: str = Field(..., description="Input text to transform")
    sentinel: str = Field(default="$", description="End-of-string sentinel character")


class SearchFmIndexDTO(BaseModel):
    text: str = Field(..., description="Source text to build FM-Index")
    pattern: str = Field(..., description="Query substring to count and locate")


class SearchTrieDTO(BaseModel):
    words: List[str] = Field(..., description="Word dictionary to index into prefix trie")
    prefix: str = Field(..., description="Prefix to search")


class SearchRadixTreeDTO(BaseModel):
    keys: List[str] = Field(..., description="List of string keys to index into compressed radix tree")
    prefix: str = Field(..., description="Prefix to find")


class SearchFstDTO(BaseModel):
    entries: List[Dict[str, Any]] = Field(..., description="Sorted key-output pairs")
    query: str = Field(..., description="Exact key query to resolve")


class SearchBPlusTreeDTO(BaseModel):
    entries: List[Dict[str, Any]] = Field(..., description="Key-value entries to index")
    range_start: int = Field(..., description="Inclusive start range key")
    range_end: int = Field(..., description="Inclusive end range key")


class SearchLsmTreeDTO(BaseModel):
    operations: List[Dict[str, Any]] = Field(..., description="Sequence of PUT/DELETE operations")
    query_key: str = Field(..., description="Key to query across memtable and SSTables")


class SearchBloomFilterDTO(BaseModel):
    items: List[str] = Field(..., description="Items to insert into Bloom filter")
    test_items: List[str] = Field(..., description="Items to test for membership")
    capacity: int = Field(default=1000, description="Expected item capacity")
    error_rate: float = Field(default=0.01, description="Desired false positive probability")


class SearchXorFilterDTO(BaseModel):
    keys: List[int] = Field(..., description="64-bit integer keys to insert")
    test_keys: List[int] = Field(..., description="Keys to test for membership")


class SearchPostingListDTO(BaseModel):
    doc_ids: List[int] = Field(..., description="Document IDs in posting list")


class SearchDeltaGapEncodingDTO(BaseModel):
    doc_ids: List[int] = Field(..., description="Strictly monotonic document IDs")


class SearchVarintEncodingDTO(BaseModel):
    numbers: List[int] = Field(..., description="List of non-negative integers to encode")


class SearchBitPackingPforDeltaDTO(BaseModel):
    values: List[int] = Field(..., description="Integers to pack using PForDelta")
    bits: int = Field(default=4, description="Bits per normal element")


class SearchEliasFanoDTO(BaseModel):
    values: List[int] = Field(..., description="Monotonically increasing integer sequence")


class SearchRoaringBitmapDTO(BaseModel):
    values: List[int] = Field(..., description="Integer values to insert into Roaring Bitmap")
    query_values: List[int] = Field(..., description="Integer values to query for membership")


class SearchMergeIntersectionDTO(BaseModel):
    list_a: List[int] = Field(..., description="Sorted posting list A")
    list_b: List[int] = Field(..., description="Sorted posting list B")


class SearchGallopingIntersectionDTO(BaseModel):
    short_list: List[int] = Field(..., description="Shorter sorted integer list")
    long_list: List[int] = Field(..., description="Longer sorted integer list")


class SearchKWayMergeHeapDTO(BaseModel):
    lists: List[List[int]] = Field(..., description="Multiple sorted integer posting lists")


class SearchBlockMaxWandDTO(BaseModel):
    posting_lists: Dict[str, List[Dict[str, Any]]] = Field(..., description="Term posting lists with scores")
    query_terms: List[str] = Field(..., description="Query terms")
    top_k: int = Field(default=10, description="Top-K threshold")


class SearchRegexToTrigramDTO(BaseModel):
    regex_pattern: str = Field(..., description="Regex pattern to extract mandatory trigram clauses")


class SearchBooleanQuerySimplifierDTO(BaseModel):
    query: str = Field(..., description="Boolean query expression to simplify into DNF/CNF")


class SearchRarestFirstOrderingDTO(BaseModel):
    terms: List[str] = Field(..., description="Query terms to order")
    doc_frequencies: Dict[str, int] = Field(..., description="Document frequency per term")


class SearchCandidateVerificationDTO(BaseModel):
    candidates: List[Dict[str, Any]] = Field(..., description="Candidate matches with text and line info")
    pattern: str = Field(..., description="Verification regex or literal pattern")


class SearchEarlyTerminationDTO(BaseModel):
    scores: List[float] = Field(..., description="Candidate match scores")
    threshold: float = Field(default=0.8, description="Early termination score cutoff")
    top_k: int = Field(default=5, description="Desired top-K results count")


class SearchScatterGatherDTO(BaseModel):
    shards: List[Dict[str, Any]] = Field(..., description="Shard configurations and candidate docs")
    query: str = Field(..., description="Search query")


class SearchHedgedRequestsDTO(BaseModel):
    replicas: List[str] = Field(..., description="Available replica nodes")
    query: str = Field(..., description="Search query")
    p95_delay_ms: float = Field(default=50.0, description="Delay before dispatching hedged request")


class SearchIndexVersionedCacheDTO(BaseModel):
    key: str = Field(..., description="Cache key")
    version: int = Field(..., description="Index snapshot version")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Data payload for set actions")
    action: str = Field(default="get", description="Action: get, set, or invalidate")


class SearchTokenizerSearchDTO(BaseModel):
    code: str = Field(..., description="Source code text to tokenize")
    language: str = Field(default="python", description="Programming language")


class SearchConcreteSyntaxTreeDTO(BaseModel):
    code: str = Field(..., description="Source code to build full Concrete Syntax Tree")


class SearchAbstractSyntaxTreeDTO(BaseModel):
    code: str = Field(..., description="Source code to parse into AST")


class SearchIncrementalParserDTO(BaseModel):
    initial_code: str = Field(..., description="Base source code")
    edit: Dict[str, Any] = Field(..., description="Edit operation with start_line, end_line, and new_text")


class SearchTreeSitterQueryDTO(BaseModel):
    code: str = Field(..., description="Source code to query")
    query_pattern: str = Field(..., description="S-expression syntax query pattern")


class SearchAstGrepPatternDTO(BaseModel):
    code: str = Field(..., description="Source code")
    pattern: str = Field(..., description="Structural pattern with metavariables ($VAR)")


class SearchSemgrepEquivalenceDTO(BaseModel):
    code: str = Field(..., description="Source code")
    pattern: str = Field(..., description="Equivalence pattern with ellipsis (... or $X)")


class SearchCombyDelimiterDTO(BaseModel):
    template: str = Field(..., description="Comby matching template e.g. 'fn(:[name])'")
    source: str = Field(..., description="Source text to match against")


class SearchSubtreeHashCloneDTO(BaseModel):
    code_snippets: List[Dict[str, str]] = Field(..., description="Code snippets with id and code")


class SearchGumTreeDiffDTO(BaseModel):
    source_code: str = Field(..., description="Original AST source code")
    target_code: str = Field(..., description="Modified AST target code")


class SearchSymbolTableDTO(BaseModel):
    code: str = Field(..., description="Source code to build scoped symbol table from")


class SearchScopeGraphDTO(BaseModel):
    code: str = Field(..., description="Source code to resolve lexical scope graph")


class SearchStackGraphDTO(BaseModel):
    definitions: List[Dict[str, Any]] = Field(..., description="Symbol definitions with symbol, scope, and file")
    references: List[Dict[str, Any]] = Field(..., description="Symbol references with symbol, scope, and file")


class SearchLspProtocolDTO(BaseModel):
    request_type: str = Field(..., description="LSP method e.g. textDocument/definition, textDocument/references")
    params: Dict[str, Any] = Field(..., description="LSP protocol parameters")


class SearchScipLsifIndexDTO(BaseModel):
    symbols: List[Dict[str, Any]] = Field(..., description="SCIP/LSIF symbol definitions")
    documents: List[Dict[str, Any]] = Field(..., description="SCIP/LSIF document occurrences")


class SearchCallGraphDTO(BaseModel):
    code: str = Field(..., description="Source code to extract inter-procedural call graph")


class SearchImportDependencyGraphDTO(BaseModel):
    files: Dict[str, str] = Field(..., description="Mapping of filename to file content")


class SearchControlFlowGraphDTO(BaseModel):
    code: str = Field(..., description="Source code to construct basic block CFG")


class SearchSsaFormDTO(BaseModel):
    code: str = Field(..., description="Source code to convert to Static Single Assignment form")


class SearchDataflowWorklistDTO(BaseModel):
    cfg_nodes: List[Dict[str, Any]] = Field(..., description="CFG basic block nodes")
    cfg_edges: List[List[str]] = Field(..., description="Directed CFG edges [source, target]")


class SearchTaintAnalysisDTO(BaseModel):
    code: str = Field(..., description="Source code to analyze for taint propagation")
    sources: List[str] = Field(..., description="Tainted input sources")
    sinks: List[str] = Field(..., description="Sensitive sink functions")


class SearchDatalogCodeqlDTO(BaseModel):
    facts: List[Dict[str, Any]] = Field(..., description="Relational code facts")
    rules: List[Dict[str, Any]] = Field(..., description="Datalog deductive rules")


class SearchAstChunkingDTO(BaseModel):
    code: str = Field(..., description="Source code to chunk along AST boundaries")
    max_chunk_size: int = Field(default=500, description="Maximum characters per chunk")


class SearchCodeEmbeddingsDTO(BaseModel):
    code_snippets: List[str] = Field(..., description="Code snippets to vectorize")
    dimensions: int = Field(default=64, description="Embedding vector dimensions")



@router.post("/algos/search/walk")
def search_recursive_walk(payload: SearchWalkDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-01", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/work-stealing-walk")
def search_work_stealing_walk(payload: SearchWorkStealingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-02", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/git-aware-walk")
def search_git_aware_walk(payload: SearchGitAwareDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-03", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/glob-match")
def search_glob_match(payload: SearchGlobDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-04", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/binary-check")
def search_binary_check(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-05", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/content-type")
def search_content_type(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-06", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/size-line-check")
def search_size_line_check(payload: SearchSizeLineDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-07", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/generated-code-check")
def search_generated_code_check(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-08", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/trigram-index")
def search_trigram_index(payload: SearchTrigramDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-09", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/simd-memchr")
def search_simd_memchr(payload: SearchSimdMemchrDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-10", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/aho-corasick")
def search_aho_corasick(payload: SearchAhoCorasickDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-11", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/lazy-dfa")
def search_lazy_dfa(payload: SearchLazyDfaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-12", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/streaming-chunk-scan")
def search_streaming_chunk_scan(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-13", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/context-snippet")
def search_context_snippet(payload: SearchContextSnippetDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-14", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/mmap-scan")
def search_mmap_scan(payload: SearchMmapDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-15", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/scan")
@router.post("/algos/scan")
def scan_multipattern(payload: AlgoScanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    results = svc.scan_directory_multipattern(
        root_dir=payload.root_dir,
        patterns=payload.patterns,
        max_files=payload.max_files,
    )
    return build_success_envelope(
        data={"total_files_matched": len(results), "results": results},
        trace_id=trace_id,
    )


@router.post("/algos/search/wu-manber")
def search_wu_manber(payload: SearchWuManberDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-25", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/z-algorithm")
def search_z_algorithm(payload: SearchZAlgorithmDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-26", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/levenshtein-distance")
def search_levenshtein_distance(payload: SearchLevenshteinDistanceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-27", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/myers-bit-parallel")
def search_myers_bit_parallel(payload: SearchMyersBitParallelDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-28", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/levenshtein-automaton")
def search_levenshtein_automaton(payload: SearchLevenshteinAutomatonDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-29", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/bk-tree")
def search_bk_tree(payload: SearchBkTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-30", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/minhash-jaccard")
def search_minhash_jaccard(payload: SearchMinHashJaccardDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-31", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/fzf-fuzzy")
def search_fzf_fuzzy(payload: SearchFzfFuzzyDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-32", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/regex-parser")
def search_regex_parser(payload: SearchRegexParserDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-33", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/thompson-nfa")
def search_thompson_nfa(payload: SearchThompsonNfaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-34", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/pike-vm")
def search_pike_vm(payload: SearchPikeVmDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-35", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/backtracking-regex")
def search_backtracking_regex(payload: SearchBacktrackingRegexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-36", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/subset-dfa")
def search_subset_dfa(payload: SearchSubsetDfaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-37", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/lazy-hybrid-dfa")
def search_lazy_hybrid_dfa(payload: SearchLazyHybridDfaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-38", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/literal-extraction")
def search_literal_extraction(payload: SearchLiteralExtractionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-39", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/reverse-inner-optimizer")
def search_reverse_inner_optimizer(payload: SearchReverseInnerOptimizerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-40", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/hyperscan-regex-set")
def search_hyperscan_regex_set(payload: SearchHyperscanRegexSetDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-41", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/redos-protection")
def search_redos_protection(payload: SearchReDosProtectionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-42", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/inverted-index")
def search_inverted_index(payload: SearchInvertedIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-43", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/trigram-inverted-index")
def search_trigram_inverted_index(payload: SearchTrigramInvertedIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-44", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/positional-trigram-index")
def search_positional_trigram_index(payload: SearchPositionalTrigramIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-45", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/sparse-ngrams")
def search_sparse_ngrams(payload: SearchSparseNgramsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-46", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/suffix-array-sais")
def search_suffix_array_sais(payload: SearchSuffixArraySaisDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-47", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/lcp-array-kasai")
def search_lcp_array_kasai(payload: SearchLcpArrayKasaiDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-48", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/suffix-automaton")
def search_suffix_automaton(payload: SearchSuffixAutomatonDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-49", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/burrows-wheeler-transform")
def search_burrows_wheeler_transform(payload: SearchBurrowsWheelerTransformDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-50", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/fm-index")
def search_fm_index(payload: SearchFmIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-51", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/trie")
def search_trie(payload: SearchTrieDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-52", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/radix-tree")
def search_radix_tree(payload: SearchRadixTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-53", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/fst")
def search_fst(payload: SearchFstDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-54", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/b-plus-tree")
def search_b_plus_tree(payload: SearchBPlusTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-55", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/lsm-tree")
def search_lsm_tree(payload: SearchLsmTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-56", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/bloom-filter")
def search_bloom_filter(payload: SearchBloomFilterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-57", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/xor-filter")
def search_xor_filter(payload: SearchXorFilterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-58", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/posting-list")
def search_posting_list(payload: SearchPostingListDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-59", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/delta-gap-encoding")
def search_delta_gap_encoding(payload: SearchDeltaGapEncodingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-60", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/varint-encoding")
def search_varint_encoding(payload: SearchVarintEncodingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-61", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/pfor-delta")
def search_pfor_delta(payload: SearchBitPackingPforDeltaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-62", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/elias-fano")
def search_elias_fano(payload: SearchEliasFanoDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-63", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/roaring-bitmap")
def search_roaring_bitmap(payload: SearchRoaringBitmapDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-64", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/merge-intersection")
def search_merge_intersection(payload: SearchMergeIntersectionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-65", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/galloping-intersection")
def search_galloping_intersection(payload: SearchGallopingIntersectionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-66", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/k-way-merge-heap")
def search_k_way_merge_heap(payload: SearchKWayMergeHeapDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-67", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/block-max-wand")
def search_block_max_wand(payload: SearchBlockMaxWandDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-68", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/regex-to-trigram")
def search_regex_to_trigram(payload: SearchRegexToTrigramDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-69", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/boolean-query-simplifier")
def search_boolean_query_simplifier(payload: SearchBooleanQuerySimplifierDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-70", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/rarest-first-ordering")
def search_rarest_first_ordering(payload: SearchRarestFirstOrderingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-71", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/candidate-verification")
def search_candidate_verification(payload: SearchCandidateVerificationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-72", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/early-termination")
def search_early_termination(payload: SearchEarlyTerminationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-73", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/scatter-gather")
def search_scatter_gather(payload: SearchScatterGatherDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-74", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/hedged-requests")
def search_hedged_requests(payload: SearchHedgedRequestsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-75", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/index-versioned-cache")
def search_index_versioned_cache(payload: SearchIndexVersionedCacheDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-76", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/tokenizer-search")
def search_tokenizer_search(payload: SearchTokenizerSearchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-77", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/concrete-syntax-tree")
def search_concrete_syntax_tree(payload: SearchConcreteSyntaxTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-78", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/abstract-syntax-tree")
def search_abstract_syntax_tree(payload: SearchAbstractSyntaxTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-79", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/incremental-parser")
def search_incremental_parser(payload: SearchIncrementalParserDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-80", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/tree-sitter-query")
def search_tree_sitter_query(payload: SearchTreeSitterQueryDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-81", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/ast-grep-pattern")
def search_ast_grep_pattern(payload: SearchAstGrepPatternDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-82", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/semgrep-equivalence")
def search_semgrep_equivalence(payload: SearchSemgrepEquivalenceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-83", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/comby-delimiter")
def search_comby_delimiter(payload: SearchCombyDelimiterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-84", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/subtree-hash-clone")
def search_subtree_hash_clone(payload: SearchSubtreeHashCloneDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-85", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/gumtree-diff")
def search_gumtree_diff(payload: SearchGumTreeDiffDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-86", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/symbol-table")
def search_symbol_table(payload: SearchSymbolTableDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-87", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/scope-graph")
def search_scope_graph(payload: SearchScopeGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-88", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/stack-graph")
def search_stack_graph(payload: SearchStackGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-89", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/lsp-protocol")
def search_lsp_protocol(payload: SearchLspProtocolDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-90", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/scip-lsif-index")
def search_scip_lsif_index(payload: SearchScipLsifIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-91", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/call-graph")
def search_call_graph(payload: SearchCallGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-92", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/import-dependency-graph")
def search_import_dependency_graph(payload: SearchImportDependencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-93", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/control-flow-graph")
def search_control_flow_graph(payload: SearchControlFlowGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-94", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/ssa-form")
def search_ssa_form(payload: SearchSsaFormDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-95", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/dataflow-worklist")
def search_dataflow_worklist(payload: SearchDataflowWorklistDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-96", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/taint-analysis")
def search_taint_analysis(payload: SearchTaintAnalysisDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-97", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/datalog-codeql")
def search_datalog_codeql(payload: SearchDatalogCodeqlDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-98", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/ast-chunking")
def search_ast_chunking(payload: SearchAstChunkingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-99", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/code-embeddings")
def search_code_embeddings(payload: SearchCodeEmbeddingsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-100", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


