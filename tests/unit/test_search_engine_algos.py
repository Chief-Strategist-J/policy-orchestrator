"""
Module: test_search_engine_algos
Unit Tests: Complete Coverage of Algorithms 01 through 22
"""

import os
import tempfile
import unittest

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


class TestSearchEngineAlgorithms(unittest.TestCase):
    def test_algo_01_recursive_walk(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "test.txt")
            with open(f1, "w") as f:
                f.write("hello")
            paths = SearchEngineRecursiveWalkAlgo.execute(tmpdir)
            self.assertIn(f1, paths)

    def test_algo_02_work_stealing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "a.py")
            with open(f1, "w") as f:
                f.write("print('hello')")
            entries = SearchEngineWorkStealingWalkerAlgo.execute(tmpdir, max_workers=2)
            self.assertIn(f1, entries)

    def test_algo_03_git_aware_walker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, ".git"))
            ignored = os.path.join(tmpdir, "ignored.log")
            tracked = os.path.join(tmpdir, "main.py")
            with open(os.path.join(tmpdir, ".gitignore"), "w") as f:
                f.write("*.log\n")
            with open(ignored, "w") as f:
                f.write("logs")
            with open(tracked, "w") as f:
                f.write("print(1)")
            paths = SearchEngineGitAwareWalkerAlgo.execute(tmpdir)
            self.assertIn(tracked, paths)
            self.assertNotIn(ignored, paths)

    def test_algo_04_glob_matcher(self):
        matched = SearchEngineGlobMatcherAlgo.execute("*.ts", ["src/app.ts", "src/app.py"])
        self.assertEqual(matched, ["src/app.ts"])

    def test_algo_05_binary_classifier(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            f.write(b"ELF\x00\x01\x02")
            bin_path = f.name
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            f.write(b"def main(): pass\n")
            txt_path = f.name
        try:
            self.assertFalse(SearchEngineBinaryClassifierAlgo.is_text_file(bin_path))
            self.assertTrue(SearchEngineBinaryClassifierAlgo.is_text_file(txt_path))
        finally:
            os.remove(bin_path)
            os.remove(txt_path)

    def test_algo_06_content_type_prober(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
            f.write("print('hello')")
            py_path = f.name
        try:
            self.assertEqual(SearchEngineContentTypeProberAlgo.probe(py_path), "python")
        finally:
            os.remove(py_path)

    def test_algo_07_size_line_bouncer(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("line1\nline2\n")
            fpath = f.name
        try:
            allowed, _ = SearchEngineSizeLineBouncerAlgo.check_limits(fpath, max_bytes=1000, max_lines=10)
            self.assertTrue(allowed)
            disallowed, _ = SearchEngineSizeLineBouncerAlgo.check_limits(fpath, max_bytes=2)
            self.assertFalse(disallowed)
        finally:
            os.remove(fpath)

    def test_algo_08_generated_code_classifier(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("// Code generated by protoc-gen-go. DO NOT EDIT.\npackage test\n")
            gen_path = f.name
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("def my_custom_code(): pass\n")
            custom_path = f.name
        try:
            self.assertTrue(SearchEngineGeneratedCodeClassifierAlgo.is_generated(gen_path))
            self.assertFalse(SearchEngineGeneratedCodeClassifierAlgo.is_generated(custom_path))
        finally:
            os.remove(gen_path)
            os.remove(custom_path)

    def test_algo_09_trigram_index(self):
        idx = SearchEngineTrigramIndexAlgo()
        idx.index_file("doc1", "apple banana cherry")
        self.assertEqual(idx.query_candidates("banana"), {"doc1"})
        self.assertEqual(idx.query_candidates("zebra"), set())

    def test_algo_10_simd_memchr(self):
        offsets = SearchEngineSimdMemchrAlgo.find_all_occurrences("abc def abc ghi", "abc")
        self.assertEqual(offsets, [0, 8])

    def test_algo_11_aho_corasick(self):
        ac = SearchEngineAhoCorasickAlgo(["he", "she", "his", "hers"])
        matches = ac.find_matches("ushers")
        patterns_found = [m[2] for m in matches]
        self.assertIn("she", patterns_found)
        self.assertIn("he", patterns_found)
        self.assertIn("hers", patterns_found)

    def test_algo_12_lazy_dfa(self):
        matches = SearchEngineLazyDfaAlgo.match_all("def foo():\n    pass\ndef bar():\n    pass", r"def\s+([a-zA-Z0-9_]+)")
        self.assertEqual(len(matches), 2)

    def test_algo_13_streaming_chunk_scanner(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("the quick brown fox jumps over the lazy dog")
            fpath = f.name
        try:
            matches = SearchEngineStreamingChunkScannerAlgo.scan_file_chunks(fpath, "fox", chunk_size=10)
            self.assertEqual(len(matches), 1)
        finally:
            os.remove(fpath)

    def test_algo_14_context_snippet_collector(self):
        lines = ["line1", "line2", "line3 TARGET", "line4", "line5"]
        res = SearchEngineContextSnippetCollectorAlgo.collect_snippet(lines, target_line_1_indexed=3, lines_before=1, lines_after=1)
        snippet = res["formatted_snippet"]
        self.assertIn("line2", snippet)
        self.assertIn("line3 TARGET", snippet)
        self.assertIn("line4", snippet)

    def test_algo_15_mmap_scanner(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("quick brown fox jumps over lazy dog")
            tmpname = f.name
        try:
            matches = SearchEngineMmapScannerAlgo.scan_file(tmpname, "fox")
            self.assertEqual(len(matches), 1)
        finally:
            os.remove(tmpname)

    def test_algo_16_position_span_tracker(self):
        tracker = PositionSpanTracker("line1\nline2\nline3")
        span = tracker.compute_span(6, 11)
        self.assertEqual(span.start_line, 2)
        self.assertEqual(span.start_col, 1)

    def test_algo_17_tree_sitter_ast(self):
        extractor = AstExtractor()
        code = "class Greeter:\n    def greet(self, name):\n        return 'hello ' + name\n"
        ast_root = extractor.parse_python(code)
        classes = extractor.find_nodes(ast_root, "ClassDef")
        functions = extractor.find_nodes(ast_root, "FunctionDef")
        self.assertEqual(len(classes), 1)
        self.assertEqual(len(functions), 1)
        self.assertEqual(classes[0].name, "Greeter")
        self.assertEqual(functions[0].name, "greet")

    def test_algo_18_cst_matcher(self):
        matcher = CstMatcher("def $NAME($ARGS):")
        code = "def calculate_sum(a, b):\n    return a + b\n"
        matches = matcher.find_matches(code)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].captures.get("NAME"), "calculate_sum")

    def test_algo_19_symbol_scope_resolver(self):
        resolver = SymbolScopeResolver()
        code = "x = 10\ndef foo():\n    x = 20\n    return x\n"
        scope = resolver.resolve_python_scopes(code)
        shadowed = resolver.find_all_shadowed_symbols(scope)
        self.assertEqual(len(shadowed), 1)
        self.assertEqual(shadowed[0].name, "x")

    def test_algo_20_comment_extractor(self):
        extractor = CommentExtractor()
        code_clean = '"""Top docblock."""\ndef foo():\n    return 42\n'
        res_clean = extractor.lint_zero_inline_comment_doctrine(code_clean)
        self.assertTrue(res_clean.is_compliant)

        code_violation = 'def foo():\n    # inline comment\n    return 42\n'
        res_violation = extractor.lint_zero_inline_comment_doctrine(code_violation)
        self.assertFalse(res_violation.is_compliant)

    def test_algo_21_import_dependency_grapher(self):
        grapher = ImportDependencyGrapher()
        grapher.add_module_from_source("mod_a", "import mod_b")
        grapher.add_module_from_source("mod_b", "import mod_c")
        grapher.add_module_from_source("mod_c", "pass")
        report = grapher.build_report()
        self.assertFalse(report.has_cycles)
        self.assertIn("mod_c", report.topological_order)

    def test_algo_22_code_outline_generator(self):
        generator = CodeOutlineGenerator()
        code = 'class Service:\n    """Main service."""\n    def run(self):\n        pass\n'
        outline = generator.generate_python_outline("service.py", code)
        self.assertEqual(len(outline.symbols), 1)
        self.assertEqual(outline.symbols[0].name, "Service")
        md = generator.format_as_markdown(outline)
        self.assertIn("Service", md)


if __name__ == "__main__":
    unittest.main()
