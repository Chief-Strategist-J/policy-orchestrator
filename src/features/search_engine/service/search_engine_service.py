"""
Module: search_engine_service
Architecture: Unified Search Engine Domain Service

Blueprint:
- Exposes access to categorized Search, Observability, and Update algorithms.
- Orchestrates recursive file walks, binary classification, Aho-Corasick scans, AST extraction, and atomic patching.
- Follows Hexagonal Architecture and the Zero-Inline-Comment Doctrine.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

from src.features.search_engine.algos.search import (
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

from src.features.search_engine.algos.observability import (
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

from src.features.search_engine.algos.update import (
    CstMatcher,
    CstMatch,
    UpdateBatchPatcherAlgo,
    PatchOperation,
    PatchResult,
    UpdateDiffEngineAlgo,
    UnifiedDiffResult,
)


class SearchEngineService:
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
                    header = f.read(1024)
                    if self.binary_classifier.is_text_file(file_path) is False:
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
