"""
Module: test_search_algos_25_50
Unit Tests: Complete Coverage of Search Algorithms ALGO-SRCH-25 through ALGO-SRCH-50
"""

import unittest
from src.features.code_engine.algos.search import (
    SearchEngineWuManberAlgo,
    SearchEngineZAlgorithmAlgo,
    SearchEngineLevenshteinDistanceAlgo,
    SearchEngineMyersBitParallelAlgo,
    SearchEngineLevenshteinAutomatonAlgo,
    SearchEngineBkTreeAlgo,
    SearchEngineMinHashJaccardAlgo,
    SearchEngineFzfFuzzyAlgo,
    SearchEngineRegexParserAlgo,
    SearchEngineThompsonNfaAlgo,
    SearchEnginePikeVmAlgo,
    SearchEngineBacktrackingRegexAlgo,
    SearchEngineSubsetDfaAlgo,
    SearchEngineLazyHybridDfaAlgo,
    SearchEngineLiteralExtractionAlgo,
    SearchEngineReverseInnerOptimizerAlgo,
    SearchEngineHyperscanRegexSetAlgo,
    SearchEngineReDosProtectionAlgo,
    SearchEngineInvertedIndexAlgo,
    SearchEngineTrigramInvertedIndexAlgo,
    SearchEnginePositionalTrigramIndexAlgo,
    SearchEngineSparseNgramsAlgo,
    SearchEngineSuffixArraySaisAlgo,
    SearchEngineLcpArrayKasaiAlgo,
    SearchEngineSuffixAutomatonAlgo,
    SearchEngineBurrowsWheelerTransformAlgo,
)


class TestSearchAlgorithms25To50(unittest.TestCase):
    def test_algo_25_wu_manber(self):
        text = "the quick brown fox jumps over the lazy dog"
        patterns = ["quick", "fox", "lazy", "missing"]
        res = SearchEngineWuManberAlgo.execute(text, patterns=patterns, block_size=2)
        matched_patterns = {m["pattern"] for m in res}
        self.assertIn("quick", matched_patterns)
        self.assertIn("fox", matched_patterns)
        self.assertIn("lazy", matched_patterns)
        self.assertNotIn("missing", matched_patterns)

    def test_algo_26_z_algorithm(self):
        text = "abracadabra"
        pattern = "abra"
        res = SearchEngineZAlgorithmAlgo.execute(text, pattern=pattern)
        self.assertEqual(len(res["matches"]), 2)
        self.assertEqual(res["matches"][0]["start_offset"], 0)
        self.assertEqual(res["matches"][1]["start_offset"], 7)

    def test_algo_27_levenshtein_distance(self):
        res = SearchEngineLevenshteinDistanceAlgo.execute(source="kitten", target="sitting", include_matrix=True)
        self.assertEqual(res["distance"], 3)
        self.assertGreater(res["similarity_ratio"], 0.5)
        self.assertTrue(len(res["operations"]) > 0)
        self.assertIn("dp_matrix", res)

    def test_algo_28_myers_bit_parallel(self):
        text = "hello world and code engine"
        res = SearchEngineMyersBitParallelAlgo.execute(text, pattern="word", max_distance=1)
        self.assertTrue(len(res) > 0)
        self.assertTrue(any(m["distance"] <= 1 for m in res))

    def test_algo_29_levenshtein_automaton(self):
        candidates = ["user", "uses", "used", "account", "useful"]
        res = SearchEngineLevenshteinAutomatonAlgo.execute(pattern="user", candidates=candidates, max_distance=1)
        accepted = [r["candidate"] for r in res]
        self.assertIn("user", accepted)
        self.assertIn("uses", accepted)
        self.assertIn("used", accepted)
        self.assertNotIn("account", accepted)

    def test_algo_30_bk_tree(self):
        words = ["book", "books", "cake", "boo", "boon", "cook", "cart"]
        res = SearchEngineBkTreeAlgo.execute(dictionary=words, query="book", max_distance=1)
        matched = [r["word"] for r in res]
        self.assertIn("book", matched)
        self.assertIn("books", matched)
        self.assertIn("boo", matched)
        self.assertIn("boon", matched)
        self.assertIn("cook", matched)
        self.assertNotIn("cart", matched)

    def test_algo_31_minhash_jaccard(self):
        docs = [
            {"id": "doc1", "text": "def calculate_tax(amount): return amount * 0.2"},
            {"id": "doc2", "text": "def calculate_tax(amount): return amount * 0.20"},
            {"id": "doc3", "text": "import sys; print(sys.version)"},
        ]
        res = SearchEngineMinHashJaccardAlgo.execute(documents=docs, similarity_threshold=0.4)
        pairs = res["candidate_pairs"]
        self.assertTrue(len(pairs) >= 1)
        self.assertEqual(pairs[0]["doc_a"], "doc1")
        self.assertEqual(pairs[0]["doc_b"], "doc2")

    def test_algo_32_fzf_fuzzy(self):
        candidates = [
            "src/features/code_engine/service.py",
            "src/api/rest/v1/routers/search_router.py",
            "tests/unit/test_code_engine_algos.py",
        ]
        res = SearchEngineFzfFuzzyAlgo.execute(candidates=candidates, query="cesrv")
        self.assertTrue(len(res) >= 1)
        self.assertEqual(res[0]["candidate"], "src/features/code_engine/service.py")

    def test_algo_33_regex_parser(self):
        res = SearchEngineRegexParserAlgo.execute("abc(def|ghi)+[0-9]*")
        self.assertTrue(res["is_valid"])
        self.assertIsNotNone(res["ast"])
        self.assertEqual(res["ast"]["type"], "concatenation")

    def test_algo_34_thompson_nfa(self):
        res = SearchEngineThompsonNfaAlgo.execute("a(b|c)*d")
        self.assertGreater(res["state_count"], 4)
        self.assertIsNotNone(res["start_state_id"])
        self.assertIsNotNone(res["match_state_id"])

    def test_algo_35_pike_vm(self):
        text = "abc123xyz"
        res = SearchEnginePikeVmAlgo.execute(text=text, pattern="c123x")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["matched_text"], "c123x")

    def test_algo_36_backtracking_regex(self):
        text = "foo123 bar456 baz789"
        res = SearchEngineBacktrackingRegexAlgo.execute(text=text, pattern=r"(?<=foo)\d+")
        self.assertEqual(len(res["matches"]), 1)
        self.assertEqual(res["matches"][0]["matched_text"], "123")
        self.assertFalse(res["budget_exceeded"])

    def test_algo_37_subset_dfa(self):
        text = "abcab"
        res = SearchEngineSubsetDfaAlgo.execute(text=text, pattern="ab")
        self.assertEqual(len(res["matches"]), 2)
        self.assertGreater(res["dfa_state_count"], 1)

    def test_algo_38_lazy_hybrid_dfa(self):
        text = "hello world and code"
        res = SearchEngineLazyHybridDfaAlgo.execute(text=text, pattern="world")
        self.assertEqual(len(res["matches"]), 1)
        self.assertEqual(res["engine_used"], "lazy_dfa")

    def test_algo_39_literal_extraction(self):
        res = SearchEngineLiteralExtractionAlgo.execute(r"fetch\w+Async")
        self.assertEqual(res["required_prefix"], "fetch")
        self.assertTrue(res["can_use_literal_prefilter"])
        self.assertIn("Async", res["all_extracted_literals"])

    def test_algo_40_reverse_inner_optimizer(self):
        text = "class UserAccountException(BaseException): pass"
        res = SearchEngineReverseInnerOptimizerAlgo.execute(text=text, pattern=r"\w+Exception")
        self.assertTrue(len(res["matches"]) > 0)
        self.assertEqual(res["matches"][0]["matched_text"], "UserAccountException")

    def test_algo_41_hyperscan_regex_set(self):
        text = "eval(code) and os.system('ls') with password = '123'"
        rules = [
            {"id": "RULE-EVAL", "pattern": r"eval\("},
            {"id": "RULE-SYS", "pattern": r"os\.system\("},
            {"id": "RULE-SECRET", "pattern": r"password\s*="},
        ]
        res = SearchEngineHyperscanRegexSetAlgo.execute(text=text, rules=rules)
        self.assertEqual(res["total_hits"], 3)
        rule_ids = {m["rule_id"] for m in res["matches"]}
        self.assertEqual(rule_ids, {"RULE-EVAL", "RULE-SYS", "RULE-SECRET"})

    def test_algo_42_redos_protection(self):
        vuln_res = SearchEngineReDosProtectionAlgo.execute(r"(a+)+$")
        self.assertTrue(vuln_res["is_vulnerable"])
        self.assertEqual(vuln_res["severity"], "CRITICAL")

        safe_res = SearchEngineReDosProtectionAlgo.execute(r"^[a-zA-Z0-9_-]+$")
        self.assertFalse(safe_res["is_vulnerable"])
        self.assertEqual(safe_res["severity"], "SAFE")

    def test_algo_43_inverted_index(self):
        docs = [
            {"id": "f1.py", "text": "import os\nimport sys\ndef run(): pass"},
            {"id": "f2.py", "text": "import sys\nimport json\ndef parse(): pass"},
            {"id": "f3.py", "text": "import os\ndef test(): pass"},
        ]
        res_and = SearchEngineInvertedIndexAlgo.execute(documents=docs, query_terms=["import", "sys"], operation="AND")
        self.assertEqual(res_and["matched_doc_ids"], ["f1.py", "f2.py"])

        res_or = SearchEngineInvertedIndexAlgo.execute(documents=docs, query_terms=["json", "test"], operation="OR")
        self.assertEqual(res_or["matched_doc_ids"], ["f2.py", "f3.py"])

    def test_algo_44_trigram_inverted_index(self):
        docs = [
            {"id": "a.txt", "text": "hello world"},
            {"id": "b.txt", "text": "world wide web"},
            {"id": "c.txt", "text": "foo bar baz"},
        ]
        res = SearchEngineTrigramInvertedIndexAlgo.execute(documents=docs, query="world")
        self.assertIn("a.txt", res["candidate_doc_ids"])
        self.assertIn("b.txt", res["candidate_doc_ids"])
        self.assertNotIn("c.txt", res["candidate_doc_ids"])

    def test_algo_45_positional_trigram_index(self):
        docs = [
            {"id": "doc1", "text": "the quick brown fox"},
            {"id": "doc2", "text": "the brown quick fox"},
        ]
        res = SearchEnginePositionalTrigramIndexAlgo.execute(documents=docs, query="quick brown")
        matched_docs = [r["doc_id"] for r in res]
        self.assertIn("doc1", matched_docs)
        self.assertNotIn("doc2", matched_docs)

    def test_algo_46_sparse_ngrams(self):
        text = "AuthenticationManagerMiddlewareHandler"
        res = SearchEngineSparseNgramsAlgo.execute(text=text, min_gram_len=3, max_gram_len=6)
        self.assertTrue(res["total_grams"] > 0)
        self.assertTrue(len(res["extracted_grams"]) > 0)

    def test_algo_47_suffix_array(self):
        text = "banana"
        res = SearchEngineSuffixArraySaisAlgo.execute(text=text, pattern="an")
        self.assertEqual(res["occurrence_count"], 2)
        self.assertEqual(res["matches"], [1, 3])

    def test_algo_48_lcp_array(self):
        text = "banana"
        res = SearchEngineLcpArrayKasaiAlgo.execute(text=text)
        self.assertEqual(res["longest_repeated_substring"], "ana")
        self.assertEqual(res["max_lcp"], 3)

    def test_algo_49_suffix_automaton(self):
        text = "abracadabra"
        res_found = SearchEngineSuffixAutomatonAlgo.execute(text=text, query="cadabra")
        self.assertTrue(res_found["contains_pattern"])

        res_missing = SearchEngineSuffixAutomatonAlgo.execute(text=text, query="xyz")
        self.assertFalse(res_missing["contains_pattern"])
        self.assertGreater(res_found["distinct_substring_count"], 10)

    def test_algo_50_burrows_wheeler_transform(self):
        text = "banana"
        res = SearchEngineBurrowsWheelerTransformAlgo.execute(text=text, sentinel="$")
        self.assertEqual(res["reconstructed_text"], "banana")
        self.assertTrue(len(res["bwt_string"]) > 0)


if __name__ == "__main__":
    unittest.main()
