"""
================================================================================
UNIT TESTS: CODE ENGINE SYNTAX MUTATION ALGORITHMS (PART 3)
================================================================================
"""

import pytest
from src.features.code_engine.algos.syntax_mutation import (
    CodeEngineLosslessSyntaxTreeAlgo,
    CodeEngineRedGreenTreeAlgo,
    CodeEngineTriviaAttachmentAlgo,
    CodeEngineTreeRewriterAlgo,
    CodeEngineSemanticPatchAlgo,
    CodeEngineImportManagerAlgo,
    CodeEngineRenameRefactoringAlgo,
)


def test_lossless_syntax_tree():
    code = "# Header comment\ndef foo():\n    return 42\n"
    algo = CodeEngineLosslessSyntaxTreeAlgo()
    res = algo.execute({"source_code": code})
    assert res["algorithm"] == "ALGO-SYNX-127"
    assert res["is_round_trip_lossless"] is True
    assert res["reconstructed_code"] == code


def test_red_green_tree():
    code = "x = 10\ny = 20\n"
    algo = CodeEngineRedGreenTreeAlgo()
    res = algo.execute({"source_code": code})
    assert res["algorithm"] == "ALGO-SYNX-128"
    assert res["total_width"] == len(code)
    assert res["green_node_count"] >= 2


def test_trivia_attachment():
    code = "import os\n# helper comment\nx = 1\n"
    algo = CodeEngineTriviaAttachmentAlgo()
    res = algo.execute({"source_code": code})
    assert res["algorithm"] == "ALGO-SYNX-129"
    assert res["trivia_count"] >= 1


def test_tree_rewriter():
    code = "def main():\n    legacy_call(1, 2)\n"
    algo = CodeEngineTreeRewriterAlgo()
    res = algo.execute({
        "source_code": code,
        "target_function": "legacy_call",
        "replacement_function": "modern_call",
    })
    assert res["algorithm"] == "ALGO-SYNX-131"
    assert "modern_call" in res["transformed_code"]
    assert res["transform_count"] == 1


def test_semantic_patch():
    code = "def check(x):\n    assert x == True\n"
    algo = CodeEngineSemanticPatchAlgo()
    res = algo.execute({
        "source_code": code,
        "pattern": "assert $X == True",
        "replacement": "assert $X",
    })
    assert res["algorithm"] == "ALGO-SYNX-133"
    assert res["match_count"] >= 1


def test_import_manager():
    code = "import sys\nimport os\nfrom src.domain import model\nimport requests\n\ndef run():\n    pass\n"
    algo = CodeEngineImportManagerAlgo()
    res = algo.execute({"source_code": code})
    assert res["algorithm"] == "ALGO-SYNX-137"
    assert res["total_imports"] >= 4
    assert res["is_modified"] is True


def test_rename_refactoring():
    code = "def calculate(factor):\n    return factor * 2\n"
    algo = CodeEngineRenameRefactoringAlgo()
    res = algo.execute({
        "source_code": code,
        "old_name": "factor",
        "new_name": "multiplier",
    })
    assert res["algorithm"] == "ALGO-SYNX-138"
    assert "multiplier" in res["refactored_code"]
    assert res["renamed_occurrences"] >= 2
