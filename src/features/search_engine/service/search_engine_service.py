"""
Module: search_engine_service
Architecture: Unified Search Engine Domain Service

Blueprint:
- Exposes access to all 22 core search and analysis algorithms.
- Orchestrates recursive file walks, binary classification, Aho-Corasick multi-pattern scans, and AST extraction.
- Follows Hexagonal Architecture and the Zero-Inline-Comment Doctrine.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

from src.features.search_engine.algos.search_engine_algo_recursive_walk import SearchEngineRecursiveWalkAlgo
from src.features.search_engine.algos.search_engine_algo_work_stealing_walker import SearchEngineWorkStealingWalkerAlgo
from src.features.search_engine.algos.search_engine_algo_git_aware_walker import SearchEngineGitAwareWalkerAlgo
from src.features.search_engine.algos.search_engine_algo_glob_matcher import SearchEngineGlobMatcherAlgo
from src.features.search_engine.algos.search_engine_algo_binary_classifier import SearchEngineBinaryClassifierAlgo
from src.features.search_engine.algos.search_engine_algo_content_type_prober import SearchEngineContentTypeProberAlgo
from src.features.search_engine.algos.search_engine_algo_size_line_bouncer import SearchEngineSizeLineBouncerAlgo
from src.features.search_engine.algos.search_engine_algo_generated_code_classifier import SearchEngineGeneratedCodeClassifierAlgo
from src.features.search_engine.algos.search_engine_algo_trigram_index import SearchEngineTrigramIndexAlgo
from src.features.search_engine.algos.search_engine_algo_simd_memchr import SearchEngineSimdMemchrAlgo
from src.features.search_engine.algos.search_engine_algo_aho_corasick import SearchEngineAhoCorasickAlgo
from src.features.search_engine.algos.search_engine_algo_lazy_dfa import SearchEngineLazyDfaAlgo
from src.features.search_engine.algos.search_engine_algo_streaming_chunk_scanner import SearchEngineStreamingChunkScannerAlgo
from src.features.search_engine.algos.search_engine_algo_context_snippet_collector import SearchEngineContextSnippetCollectorAlgo
from src.features.search_engine.algos.search_engine_algo_mmap_scanner import SearchEngineMmapScannerAlgo
from src.features.search_engine.algos.search_engine_algo_position_span_tracker import PositionSpanTracker
from src.features.search_engine.algos.search_engine_algo_tree_sitter_ast import AstExtractor
from src.features.search_engine.algos.search_engine_algo_cst_matcher import CstMatcher
from src.features.search_engine.algos.search_engine_algo_symbol_scope_resolver import SymbolScopeResolver
from src.features.search_engine.algos.search_engine_algo_comment_extractor import CommentExtractor
from src.features.search_engine.algos.search_engine_algo_import_dependency_grapher import ImportDependencyGrapher
from src.features.search_engine.algos.search_engine_algo_code_outline_generator import CodeOutlineGenerator


class SearchEngineService:
    def __init__(self) -> None:
        self.binary_classifier = SearchEngineBinaryClassifierAlgo
        self.content_type_prober = SearchEngineContentTypeProberAlgo
        self.generated_code_classifier = SearchEngineGeneratedCodeClassifierAlgo
        self.ast_extractor = AstExtractor()
        self.scope_resolver = SymbolScopeResolver()
        self.comment_extractor = CommentExtractor()
        self.outline_generator = CodeOutlineGenerator()

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
                    header = f.read(1024)
                    if self.binary_classifier.is_binary(header):
                        continue
                    f.seek(0)
                    content = f.read().decode("utf-8", errors="ignore")

                matches = ac.search(content)
                if matches:
                    collector = SearchEngineContextSnippetCollectorAlgo(content)
                    snippets = []
                    for m in matches:
                        line_num = content[:m.start_index].count("\n") + 1
                        snippets.append({
                            "pattern": m.pattern,
                            "line": line_num,
                            "context": collector.collect(line_num, 1, 1).snippet,
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
