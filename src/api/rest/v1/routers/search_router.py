"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 SEARCH ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the 15 Layer 1 Search Algorithms
   (ALGO-SRCH-01 through ALGO-SRCH-15):
   - Fast file tree discovery (walk, work-stealing, git-aware)
   - Pattern matching (glob, binary check, content type, size/line bouncer)
   - Regex & multi-pattern indexing (trigram, simd-memchr, aho-corasick, lazy-dfa)
   - High-throughput scanning (streaming chunk, context snippet, mmap, multipattern scan)

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
