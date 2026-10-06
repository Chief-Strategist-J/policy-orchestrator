"""
================================================================================
UNIT TESTS: CODE ENGINE DIFF ALGORITHMS (PART 3)
================================================================================
"""

import pytest
from src.features.code_engine.algos.diff import (
    CodeEngineLcsDpDiffAlgo,
    CodeEngineMyersDiffAlgo,
    CodeEngineLinearMyersDiffAlgo,
    CodeEnginePatienceDiffAlgo,
    CodeEngineHistogramDiffAlgo,
    CodeEngineLineHashingInterningAlgo,
    CodeEngineUnifiedDiffAlgo,
    CodeEngineSearchReplaceBlockAlgo,
    CodeEngineWordCharRefinementAlgo,
    CodeEngineThreeWayMergeAlgo,
    CodeEngineFuzzyPatchAlgo,
)


def test_lcs_dp_diff():
    algo = CodeEngineLcsDpDiffAlgo()
    res = algo.execute({"source_lines": ["a", "b", "c"], "target_lines": ["a", "x", "c"]})
    assert res["algorithm"] == "ALGO-DIFF-145"
    assert res["lcs_length"] == 2


def test_myers_diff():
    algo = CodeEngineMyersDiffAlgo()
    res = algo.execute({"source_lines": ["A", "B", "C", "A", "B", "B", "A"], "target_lines": ["C", "B", "A", "B", "A", "C"]})
    assert res["algorithm"] == "ALGO-DIFF-146"
    assert res["edit_distance"] >= 1
    assert len(res["diff_hunks"]) > 0


def test_linear_myers_diff():
    algo = CodeEngineLinearMyersDiffAlgo()
    res = algo.execute({"source_lines": ["x = 1", "y = 2", "z = 3"], "target_lines": ["x = 1", "y = 20", "z = 3"]})
    assert res["algorithm"] == "ALGO-DIFF-147"
    assert res["total_operations"] >= 3


def test_patience_diff():
    algo = CodeEnginePatienceDiffAlgo()
    res = algo.execute({
        "source_lines": ["func main() {", "    println(1)", "}"],
        "target_lines": ["func main() {", "    println(2)", "}"],
    })
    assert res["algorithm"] == "ALGO-DIFF-148"
    assert len(res["edit_script"]) >= 3


def test_histogram_diff():
    algo = CodeEngineHistogramDiffAlgo()
    res = algo.execute({
        "source_lines": ["a", "b", "c", "d"],
        "target_lines": ["a", "b", "c_mod", "d"],
    })
    assert res["algorithm"] == "ALGO-DIFF-149"
    assert res["total_hunks"] >= 4


def test_line_hashing():
    algo = CodeEngineLineHashingInterningAlgo()
    res = algo.execute({"lines": ["alpha", "beta", "alpha", "gamma"]})
    assert res["algorithm"] == "ALGO-DIFF-150"
    assert res["unique_count"] == 3
    assert res["interned_tokens"][0] == res["interned_tokens"][2]


def test_unified_diff():
    patch = "--- a/test.py\n+++ b/test.py\n@@ -1,3 +1,3 @@\n def foo():\n-    return 1\n+    return 2\n"
    algo = CodeEngineUnifiedDiffAlgo()
    res = algo.execute({"patch_text": patch})
    assert res["algorithm"] == "ALGO-DIFF-124"
    assert res["total_additions"] == 1
    assert res["total_deletions"] == 1


def test_search_replace_block():
    doc = "function calculate() {\n    const tax = 0.05;\n    return price * tax;\n}"
    blocks = "<<<<<<< SEARCH\n    const tax = 0.05;\n=======\n    const tax = 0.08;\n>>>>>>> REPLACE"
    algo = CodeEngineSearchReplaceBlockAlgo()
    res = algo.execute({"document_text": doc, "blocks_text": blocks})
    assert res["algorithm"] == "ALGO-DIFF-125"
    assert res["is_success"] is True
    assert "0.08" in res["updated_text"]


def test_word_char_refinement():
    algo = CodeEngineWordCharRefinementAlgo()
    res = algo.execute({"old_line": "def process(item: int):", "new_line": "def process(item: str):"})
    assert res["algorithm"] == "ALGO-DIFF-151"
    assert res["similarity"] > 0.5


def test_three_way_merge_clean():
    base = "line 1\nline 2\nline 3"
    ours = "line 1 modified\nline 2\nline 3"
    theirs = "line 1\nline 2\nline 3 modified"
    algo = CodeEngineThreeWayMergeAlgo()
    res = algo.execute({"base_text": base, "ours_text": ours, "theirs_text": theirs})
    assert res["algorithm"] == "ALGO-DIFF-153"
    assert res["conflict_count"] == 0
    assert "line 1 modified" in res["merged_text"]
    assert "line 3 modified" in res["merged_text"]


def test_fuzzy_patch():
    doc = "function runTask() {\n    console.log('starting');\n    doWork();\n}"
    algo = CodeEngineFuzzyPatchAlgo()
    res = algo.execute({
        "text": doc,
        "search_target": "console.log('starting');",
        "replacement": "console.info('task initialized');",
    })
    assert res["algorithm"] == "ALGO-DIFF-155"
    assert res["is_applied"] is True
    assert "task initialized" in res["patched_text"]
