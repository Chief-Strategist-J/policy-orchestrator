"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: UNIFIED CODE & VECTOR ENGINE SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This domain service provides a unified, vendor-agnostic execution engine for
   all 33 Layer 1 algorithms across Search, Observability, Update, and Vector
   categories. It supports dynamic algorithm dispatch by ID (`execute_algorithm`),
   as well as specialized methods for directory scanning, AST analysis, zero-inline
   comment linting, atomic patching, unified diffs, and vector operations.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Hexagonal Architecture & Clean Separation: The service wraps domain algorithm
     implementations without introducing transport dependencies.
   - Dynamic Algorithm Dispatch: `execute_algorithm` validates input payload against
     algorithm contracts and executes the target algorithm instance.
   - Zero-Inline-Comment Doctrine: All algorithmic step definitions, parameter
     bindings, and error propagation rules are documented in this blueprint header.
     Function and method bodies remain 100% comment-free and pure.

3. ALGORITHM CATALOG DISPATCH MAP:
   - Search:
     • ALGO-SRCH-01: Recursive File Walker
     • ALGO-SRCH-02: Work-Stealing Parallel Walker
     • ALGO-SRCH-03: Git-Aware Ignore Walker
     • ALGO-SRCH-04: Fast Glob Path Matcher
     • ALGO-SRCH-05: Binary File Classifier
     • ALGO-SRCH-06: MIME/Content-Type Prober
     • ALGO-SRCH-07: Size & Line Count Bouncer
     • ALGO-SRCH-08: Generated Code Classifier
     • ALGO-SRCH-09: Trigram Inverted Index
     • ALGO-SRCH-10: SIMD-Memchr Vectorized Scanner
     • ALGO-SRCH-11: Aho-Corasick Multi-Pattern Automaton
     • ALGO-SRCH-12: Lazy DFA Regex Matcher
     • ALGO-SRCH-13: Streaming Chunk Scanner
     • ALGO-SRCH-14: Context Snippet Collector
     • ALGO-SRCH-15: Memory-Mapped Parallel Scanner
   - Observability:
     • ALGO-OBS-16: Fast Byte/UTF-8 Line-Column Span Tracker
     • ALGO-OBS-17: Language-Agnostic Tree-Sitter AST Extractor
     • ALGO-OBS-18: Lexical & Global Scope Symbol Resolver
     • ALGO-OBS-19: Zero-Inline-Comment Doctrine Comment Extractor & Linter
     • ALGO-OBS-20: Module Import Dependency Grapher & Cycle Detector
     • ALGO-OBS-21: Hierarchical Code Outline Generator
   - Update:
     • ALGO-UPD-22: CST Matcher & Safe Syntax Replacer
     • ALGO-UPD-23: Deterministic Multi-File Batch Patcher
     • ALGO-UPD-24: GNU/Git Unified Context Diff Engine
   - Vector:
     • ALGO-VEC-01: Vector L2 Normalization Engine
     • ALGO-VEC-02: Corpus Mean Centering & Anisotropy Removal
     • ALGO-VEC-03: Layer Normalization & Channel Standardization
     • ALGO-VEC-04: Min-Max & Z-Score Vector Scaling
     • ALGO-VEC-05: Matryoshka Representation Learning (MRL) Slicer
     • ALGO-VEC-06: Uniform Scalar Quantizer (SQ8 / SQ4)
     • ALGO-VEC-07: 1-Bit Binary Quantizer & Hamming Distance Engine
     • ALGO-VEC-08: Token Pooling Engine (Mean / CLS / Last-Token)
     • ALGO-VEC-09: Semantic Text Chunker & Breakpoint Detector
================================================================================
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Union

from src.features.code_engine.algos.search import (
    SearchEngineRecursiveWalkAlgo,
    SearchEngineWorkStealingWalkerAlgo,
    SearchEngineGitAwareWalkerAlgo,
    SearchEngineGlobMatcherAlgo,
    SearchEngineBinaryClassifierAlgo,
    SearchEngineContentTypeProberAlgo,
    SearchEngineSizeLineBouncerAlgo,
    SearchEngineGeneratedCodeClassifierAlgo,
    SearchEngineTrigramIndexAlgo,
    SearchEngineSimdMemchrAlgo,
    SearchEngineAhoCorasickAlgo,
    SearchEngineLazyDfaAlgo,
    SearchEngineStreamingChunkScannerAlgo,
    SearchEngineContextSnippetCollectorAlgo,
    SearchEngineMmapScannerAlgo,
)

from src.features.code_engine.algos.observability import (
    PositionSpanTracker,
    PositionSpan,
    AstExtractor,
    AstNode,
    SymbolScopeResolver,
    Symbol,
    LexicalScope,
    CommentExtractor,
    ExtractedComment,
    CommentLintResult,
    ImportDependencyGrapher,
    ImportNode,
    DependencyGraphReport,
    CodeOutlineGenerator,
    OutlineSymbol,
    FileOutline,
)

from src.features.code_engine.algos.update import (
    CstMatcher,
    CstMatch,
    UpdateBatchPatcherAlgo,
    PatchOperation,
    PatchResult,
    UpdateDiffEngineAlgo,
    UnifiedDiffResult,
)

from src.features.code_engine.algos.vector import (
    VectorAlgoL2Normalization,
    VectorAlgoMeanCentering,
    VectorAlgoLayerNorm,
    VectorAlgoMinMaxZScore,
    VectorAlgoMatryoshkaSlicing,
    VectorAlgoScalarQuantization,
    QuantizedVector,
    VectorAlgoBinaryQuantization,
    VectorAlgoTokenPooling,
    VectorAlgoSemanticChunker,
    TextChunk,
)


class CodeEngineService:
    def __init__(self) -> None:
        self.binary_classifier = SearchEngineBinaryClassifierAlgo
        self.content_type_prober = SearchEngineContentTypeProberAlgo
        self.generated_code_classifier = SearchEngineGeneratedCodeClassifierAlgo
        self.ast_extractor = AstExtractor()
        self.scope_resolver = SymbolScopeResolver()
        self.comment_extractor = CommentExtractor()
        self.outline_generator = CodeOutlineGenerator()
        self.patcher = UpdateBatchPatcherAlgo
        self.diff_engine = UpdateDiffEngineAlgo

    def scan_directory_multipattern(
        self,
        root_dir: str,
        patterns: List[str],
        max_files: int = 1000,
    ) -> List[Dict[str, Any]]:
        files = SearchEngineGitAwareWalkerAlgo.execute(root_dir)
        ac = SearchEngineAhoCorasickAlgo(patterns)
        results: List[Dict[str, Any]] = []

        for file_path in files[:max_files]:
            if not os.path.isfile(file_path):
                continue
            try:
                with open(file_path, "rb") as f:
                    if self.binary_classifier.is_binary_file(file_path):
                        continue
                    f.seek(0)
                    content = f.read().decode("utf-8", errors="ignore")

                matches = ac.find_matches(content)
                if matches:
                    lines = content.splitlines()
                    snippets = []
                    for m in matches:
                        line_num = content[:m[0]].count("\n") + 1
                        res = SearchEngineContextSnippetCollectorAlgo.collect_snippet(lines, line_num, 1, 1)
                        snippets.append({
                            "pattern": m[2],
                            "line": line_num,
                            "context": res["formatted_snippet"],
                        })
                    results.append({
                        "file": file_path,
                        "match_count": len(matches),
                        "matches": snippets,
                    })
            except Exception:
                continue

        return results

    def inspect_file_outline(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        outline = self.outline_generator.generate_python_outline(file_path, code)
        md = self.outline_generator.format_as_markdown(outline)
        return {
            "file": file_path,
            "total_lines": outline.total_lines,
            "symbols_count": len(outline.symbols),
            "markdown": md,
        }

    def analyze_module_dependencies(self, directory: str) -> Dict[str, Any]:
        grapher = ImportDependencyGrapher()
        files = SearchEngineRecursiveWalkAlgo.execute(directory, allowed_extensions={".py"})
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                mod_name = os.path.relpath(file_path, directory).replace(os.sep, ".").removesuffix(".py")
                grapher.add_module_from_source(mod_name, code)
            except Exception:
                continue
        report = grapher.build_report()
        return {
            "total_modules": report.total_modules,
            "total_edges": report.total_edges,
            "has_cycles": report.has_cycles,
            "cycles": report.cycles,
            "topological_order": report.topological_order,
            "orphan_modules": report.orphan_modules,
        }

    def lint_zero_inline_comments(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        report = self.comment_extractor.lint_zero_inline_comment_doctrine(code)
        return {
            "file": file_path,
            "is_compliant": report.is_compliant,
            "total_comments": report.total_comments,
            "banned_inline_count": len(report.banned_inline_comments),
            "banned_comments": [
                {"line": c.start_line, "text": c.text}
                for c in report.banned_inline_comments
            ],
            "todos_count": len(report.todos_and_fixmes),
        }

    def apply_batch_patch(
        self,
        operations: List[Dict[str, Any]],
        dry_run: bool = False,
    ) -> List[Dict[str, Any]]:
        ops = [
            PatchOperation(
                file_path=op["file_path"],
                find_pattern=op["find_pattern"],
                replace_text=op["replace_text"],
                expected_sha256=op.get("expected_sha256"),
                is_regex=op.get("is_regex", False),
            )
            for op in operations
        ]
        results = self.patcher.apply_batch(ops, dry_run=dry_run)
        return [
            {
                "file_path": r.file_path,
                "success": r.success,
                "occurrences": r.occurrences,
                "before_sha256": r.before_sha256,
                "after_sha256": r.after_sha256,
                "error_message": r.error_message,
            }
            for r in results
        ]

    def generate_diff(
        self,
        original_content: str,
        modified_content: str,
        file_path: str = "file",
    ) -> Dict[str, Any]:
        res = self.diff_engine.generate_unified_diff(
            original_content=original_content,
            modified_content=modified_content,
            file_path=file_path,
        )
        return {
            "file_path": res.file_path,
            "has_changes": res.has_changes,
            "added_lines": res.added_lines,
            "deleted_lines": res.deleted_lines,
            "patch": res.patch,
        }

    def normalize_vector(self, vector: List[float], eps: float = 1e-12) -> List[float]:
        return VectorAlgoL2Normalization.normalize_single(vector, epsilon=eps)

    def center_vectors(self, vectors: List[List[float]]) -> List[List[float]]:
        centered, _ = VectorAlgoMeanCentering.center_vectors(vectors)
        return centered

    def layer_norm_vector(
        self,
        vector: List[float],
        gamma: Optional[List[float]] = None,
        beta: Optional[List[float]] = None,
        eps: float = 1e-5,
    ) -> List[float]:
        return VectorAlgoLayerNorm.normalize_single(vector, epsilon=eps, gamma=gamma, beta=beta)

    def scale_vector(
        self,
        vector: List[float],
        min_val: float = 0.0,
        max_val: float = 1.0,
        method: str = "minmax",
    ) -> List[float]:
        if method == "zscore":
            return VectorAlgoMinMaxZScore.z_score_scale(vector)
        return VectorAlgoMinMaxZScore.min_max_scale(vector, target_range=(min_val, max_val))

    def slice_vector(
        self,
        vector: List[float],
        target_dim: int,
        renormalize: bool = True,
    ) -> List[float]:
        return VectorAlgoMatryoshkaSlicing.slice_and_normalize(vector, target_dim=target_dim, renormalize_l2=renormalize)

    def quantize_scalar(self, vector: List[float], bits: int = 8) -> Dict[str, Any]:
        quantized = VectorAlgoScalarQuantization.quantize(vector, bits=bits)
        return {
            "quantized_values": quantized.quantized_values,
            "min_val": quantized.min_val,
            "max_val": quantized.max_val,
            "bits": quantized.bits,
            "dimension": len(vector),
        }

    def quantize_binary(self, vector: List[float]) -> Dict[str, Any]:
        bits = VectorAlgoBinaryQuantization.quantize_to_bits(vector)
        packed = VectorAlgoBinaryQuantization.quantize_to_packed_bytes(vector)
        return {
            "bits": bits,
            "packed_bytes_hex": packed.hex(),
            "dimension": len(vector),
        }

    def pool_tokens(
        self,
        token_embeddings: List[List[float]],
        attention_mask: Optional[List[int]] = None,
        pooling_strategy: str = "mean",
    ) -> List[float]:
        if pooling_strategy == "cls":
            return VectorAlgoTokenPooling.cls_pool(token_embeddings)
        elif pooling_strategy == "last":
            return VectorAlgoTokenPooling.last_token_pool(token_embeddings, attention_mask=attention_mask)
        return VectorAlgoTokenPooling.mean_pool(token_embeddings, attention_mask=attention_mask)

    def chunk_text(
        self,
        text: str,
        max_chunk_size: int = 200,
        overlap: int = 40,
    ) -> List[Dict[str, Any]]:
        chunks = VectorAlgoSemanticChunker.sliding_window_chunk(
            text=text,
            chunk_size=max_chunk_size,
            overlap=overlap,
        )
        return [
            {
                "chunk_index": c.chunk_index,
                "text": c.text,
                "token_count": c.token_count,
                "start_char": c.start_char,
                "end_char": c.end_char,
            }
            for c in chunks
        ]

    def execute_algorithm(
        self,
        algo_id: str,
        inputs: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        params = parameters or {}
        merged = {**inputs, **params}

        if algo_id == "ALGO-SRCH-01":
            root = merged.get("root_dir", ".")
            depth = merged.get("max_depth")
            exts = set(merged.get("allowed_extensions", [])) if merged.get("allowed_extensions") else None
            files = SearchEngineRecursiveWalkAlgo.execute(root, max_depth=depth, allowed_extensions=exts)
            return {"files": files, "count": len(files)}

        elif algo_id == "ALGO-SRCH-02":
            root = merged.get("root_dir", ".")
            workers = merged.get("workers", 4)
            files = SearchEngineWorkStealingWalkerAlgo.execute(root, workers=workers)
            return {"files": files, "count": len(files)}

        elif algo_id == "ALGO-SRCH-03":
            root = merged.get("root_dir", ".")
            ignore_files = merged.get("ignore_files")
            files = SearchEngineGitAwareWalkerAlgo.execute(root, ignore_files=ignore_files)
            return {"files": files, "count": len(files)}

        elif algo_id == "ALGO-SRCH-04":
            pattern = merged.get("pattern", "*")
            path = merged.get("path", "")
            matcher = SearchEngineGlobMatcherAlgo(pattern)
            is_match = matcher.matches(path)
            return {"pattern": pattern, "path": path, "matches": is_match}

        elif algo_id == "ALGO-SRCH-05":
            file_path = merged.get("file_path", "")
            is_bin = self.binary_classifier.is_binary_file(file_path) if file_path and os.path.isfile(file_path) else False
            return {"file_path": file_path, "is_binary": is_bin}

        elif algo_id == "ALGO-SRCH-06":
            file_path = merged.get("file_path", "")
            mime = self.content_type_prober.probe_content_type(file_path) if file_path else "application/octet-stream"
            return {"file_path": file_path, "mime_type": mime}

        elif algo_id == "ALGO-SRCH-07":
            file_path = merged.get("file_path", "")
            max_bytes = merged.get("max_bytes", 10 * 1024 * 1024)
            max_lines = merged.get("max_lines", 50000)
            ok = SearchEngineSizeLineBouncerAlgo.is_acceptable_file(file_path, max_bytes=max_bytes, max_lines=max_lines) if file_path and os.path.isfile(file_path) else True
            return {"file_path": file_path, "is_acceptable": ok}

        elif algo_id == "ALGO-SRCH-08":
            file_path = merged.get("file_path", "")
            content = merged.get("content", "")
            is_gen = self.generated_code_classifier.is_generated_code(file_path, content_sample=content)
            return {"file_path": file_path, "is_generated": is_gen}

        elif algo_id == "ALGO-SRCH-09":
            text = merged.get("text", "")
            trigrams = SearchEngineTrigramIndexAlgo.generate_trigrams(text)
            return {"text_length": len(text), "trigrams_count": len(trigrams), "trigrams": trigrams}

        elif algo_id == "ALGO-SRCH-10":
            data = merged.get("data", "").encode("utf-8") if isinstance(merged.get("data"), str) else b""
            target = ord(merged.get("byte", "\n")) if isinstance(merged.get("byte"), str) else merged.get("byte", 10)
            offsets = SearchEngineSimdMemchrAlgo.find_byte_offsets(data, target)
            return {"occurrences": len(offsets), "offsets": offsets}

        elif algo_id == "ALGO-SRCH-11":
            text = merged.get("text", "")
            patterns = merged.get("patterns", [])
            ac = SearchEngineAhoCorasickAlgo(patterns)
            raw_matches = ac.find_matches(text)
            return {
                "total_matches": len(raw_matches),
                "matches": [{"start": m[0], "end": m[1], "pattern": m[2]} for m in raw_matches],
            }

        elif algo_id == "ALGO-SRCH-12":
            pattern = merged.get("pattern", "")
            text = merged.get("text", "")
            dfa = SearchEngineLazyDfaAlgo(pattern)
            is_match = dfa.matches(text)
            return {"pattern": pattern, "matches": is_match}

        elif algo_id == "ALGO-SRCH-13":
            file_path = merged.get("file_path", "")
            chunk_size = merged.get("chunk_size", 65536)
            chunks = SearchEngineStreamingChunkScannerAlgo.read_chunks(file_path, chunk_size=chunk_size) if file_path and os.path.isfile(file_path) else []
            return {"file_path": file_path, "total_chunks": len(chunks)}

        elif algo_id == "ALGO-SRCH-14":
            lines = merged.get("lines", [])
            line_num = merged.get("line_number", 1)
            before = merged.get("lines_before", 2)
            after = merged.get("lines_after", 2)
            snip = SearchEngineContextSnippetCollectorAlgo.collect_snippet(lines, line_num, before=before, after=after)
            return snip

        elif algo_id == "ALGO-SRCH-15":
            file_path = merged.get("file_path", "")
            pattern = merged.get("pattern", "")
            matches = SearchEngineMmapScannerAlgo.scan(file_path, pattern) if file_path and os.path.isfile(file_path) else []
            return {"file_path": file_path, "matches_count": len(matches), "matches": matches}

        elif algo_id == "ALGO-OBS-16":
            content = merged.get("content", "")
            tracker = PositionSpanTracker(content)
            offset = merged.get("offset", 0)
            line, col = tracker.offset_to_line_column(offset)
            return {"offset": offset, "line": line, "column": col, "total_lines": tracker.total_lines}

        elif algo_id == "ALGO-OBS-17":
            code = merged.get("code", "")
            lang = merged.get("language", "python")
            nodes = self.ast_extractor.extract_ast_nodes(code, language=lang)
            return {
                "language": lang,
                "total_nodes": len(nodes),
                "nodes": [{"kind": n.kind, "name": n.name, "start_line": n.start_line, "end_line": n.end_line} for n in nodes],
            }

        elif algo_id == "ALGO-OBS-18":
            code = merged.get("code", "")
            ast_nodes = self.ast_extractor.extract_ast_nodes(code, language="python")
            symbols = self.scope_resolver.resolve_symbols(ast_nodes)
            return {
                "total_symbols": len(symbols),
                "symbols": [{"name": s.name, "kind": s.kind, "scope": s.scope_name, "line": s.line} for s in symbols],
            }

        elif algo_id == "ALGO-OBS-19":
            code = merged.get("code", "")
            report = self.comment_extractor.lint_zero_inline_comment_doctrine(code)
            return {
                "is_compliant": report.is_compliant,
                "total_comments": report.total_comments,
                "banned_inline_count": len(report.banned_inline_comments),
                "todos_count": len(report.todos_and_fixmes),
            }

        elif algo_id == "ALGO-OBS-20":
            directory = merged.get("directory", ".")
            return self.analyze_module_dependencies(directory)

        elif algo_id == "ALGO-OBS-21":
            file_path = merged.get("file_path", "module.py")
            code = merged.get("code", "")
            outline = self.outline_generator.generate_python_outline(file_path, code)
            return {
                "file": file_path,
                "total_lines": outline.total_lines,
                "symbols_count": len(outline.symbols),
                "markdown": self.outline_generator.format_as_markdown(outline),
            }

        elif algo_id == "ALGO-UPD-22":
            code = merged.get("code", "")
            node_type = merged.get("node_type", "function")
            matches = CstMatcher.find_nodes(code, node_type=node_type)
            return {"node_type": node_type, "matches_count": len(matches), "matches": matches}

        elif algo_id == "ALGO-UPD-23":
            operations = merged.get("operations", [])
            dry_run = merged.get("dry_run", False)
            return {"results": self.apply_batch_patch(operations, dry_run=dry_run)}

        elif algo_id == "ALGO-UPD-24":
            orig = merged.get("original_content", "")
            mod = merged.get("modified_content", "")
            path = merged.get("file_path", "file")
            return self.generate_diff(orig, mod, file_path=path)

        elif algo_id == "ALGO-VEC-01":
            vec = merged.get("vector", [])
            eps = merged.get("epsilon", merged.get("eps", 1e-12))
            normalized = self.normalize_vector(vec, eps=eps)
            return {"original_dimension": len(vec), "normalized_vector": normalized}

        elif algo_id == "ALGO-VEC-02":
            vectors = merged.get("vectors", [])
            centered = self.center_vectors(vectors)
            return {"total_vectors": len(vectors), "centered_vectors": centered}

        elif algo_id == "ALGO-VEC-03":
            vec = merged.get("vector", [])
            gamma = merged.get("gamma")
            beta = merged.get("beta")
            eps = merged.get("epsilon", merged.get("eps", 1e-5))
            norm = self.layer_norm_vector(vec, gamma=gamma, beta=beta, eps=eps)
            return {"dimension": len(vec), "normalized_vector": norm}

        elif algo_id == "ALGO-VEC-04":
            vec = merged.get("vector", [])
            min_val = merged.get("min_val", 0.0)
            max_val = merged.get("max_val", 1.0)
            method = merged.get("method", "minmax")
            scaled = self.scale_vector(vec, min_val=min_val, max_val=max_val, method=method)
            return {"scaled_vector": scaled, "method": method}

        elif algo_id == "ALGO-VEC-05":
            vec = merged.get("vector", [])
            target_dim = merged.get("target_dim", 64)
            renorm = merged.get("renormalize", True)
            sliced = self.slice_vector(vec, target_dim=target_dim, renormalize=renorm)
            return {"original_dimension": len(vec), "target_dimension": target_dim, "sliced_vector": sliced}

        elif algo_id == "ALGO-VEC-06":
            vec = merged.get("vector", [])
            bits = merged.get("bits", 8)
            return self.quantize_scalar(vec, bits=bits)

        elif algo_id == "ALGO-VEC-07":
            vec = merged.get("vector", [])
            return self.quantize_binary(vec)

        elif algo_id == "ALGO-VEC-08":
            token_embeddings = merged.get("token_embeddings", [])
            mask = merged.get("attention_mask")
            strat = merged.get("pooling_strategy", "mean")
            pooled = self.pool_tokens(token_embeddings, attention_mask=mask, pooling_strategy=strat)
            return {"pooling_strategy": strat, "pooled_vector": pooled}

        elif algo_id == "ALGO-VEC-09":
            text = merged.get("text", "")
            max_size = merged.get("max_chunk_size", 200)
            overlap = merged.get("overlap", 40)
            chunks = self.chunk_text(text, max_chunk_size=max_size, overlap=overlap)
            return {"total_chunks": len(chunks), "chunks": chunks}

        else:
            raise ValueError(f"Unknown algorithm ID: '{algo_id}'")
