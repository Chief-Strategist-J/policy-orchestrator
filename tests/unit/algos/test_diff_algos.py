"""
================================================================================
UNIT TESTS: CODE ENGINE DIFF ALGORITHMS (PART 3)
================================================================================

Tests deterministic execution for:
- LCS Dynamic Programming Diff (ALGO-DIFF-145)
================================================================================
"""

import pytest
from src.features.code_engine.algos.diff.diff_algo_lcs_dp import CodeEngineLcsDpDiffAlgo


def test_lcs_dp_diff_basic():
    source = ["def add(a, b):", "    return a + b", ""]
    target = ["def add(a, b, c=0):", "    return a + b + c", ""]

    algo = CodeEngineLcsDpDiffAlgo()
    res = algo.execute({"source_lines": source, "target_lines": target})

    assert res["algorithm"] == "ALGO-DIFF-145"
    assert res["lcs_length"] == 1
    types = [op["type"] for op in res["edit_script"]]
    assert "delete" in types
    assert "insert" in types
    assert "equal" in types


def test_lcs_dp_diff_identical():
    lines = ["import os", "import sys"]
    algo = CodeEngineLcsDpDiffAlgo()
    res = algo.execute({"source_lines": lines, "target_lines": lines})

    assert res["lcs_length"] == 2
    assert res["similarity_ratio"] == 1.0
    assert all(op["type"] == "equal" for op in res["edit_script"])
