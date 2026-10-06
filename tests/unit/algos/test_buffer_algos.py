"""
================================================================================
UNIT TESTS: CODE ENGINE BUFFER & MUTATION ALGORITHMS (PART 3)
================================================================================
"""

import pytest
from src.features.code_engine.algos.buffer import (
    CodeEngineGapBufferAlgo,
    CodeEngineRopeAlgo,
    CodeEnginePieceTableAlgo,
    CodeEngineLineIndexAlgo,
    CodeEngineUndoRedoStackAlgo,
    CodeEngineTextEditAlgo,
    CodeEngineWorkspaceEditAlgo,
    CodeEnginePositionEncodingAlgo,
    CodeEngineReverseOrderEditAlgo,
    CodeEngineIntervalTreeAlgo,
    CodeEngineEditRebasingAlgo,
    CodeEngineIdempotentEditsAlgo,
)


def test_gap_buffer_operations():
    payload = {
        "initial_text": "Hello World",
        "gap_size": 8,
        "operations": [
            {"type": "move", "position": 5},
            {"type": "insert", "text": " Beautiful"},
            {"type": "move", "position": 0},
            {"type": "insert", "text": ">>> "},
        ],
    }
    algo = CodeEngineGapBufferAlgo()
    res = algo.execute(payload)
    assert res["algorithm"] == "ALGO-BUF-139"
    assert res["text"] == ">>> Hello Beautiful World"


def test_rope_operations():
    payload = {
        "initial_text": "The quick brown fox jumps over the lazy dog",
        "operations": [
            {"type": "insert", "position": 19, "text": " swift and agile"},
            {"type": "delete", "start": 0, "length": 4},
        ],
    }
    algo = CodeEngineRopeAlgo()
    res = algo.execute(payload)
    assert res["algorithm"] == "ALGO-BUF-140"
    assert "swift and agile" in res["text"]


def test_piece_table_operations():
    payload = {
        "initial_text": "const x = 10;",
        "operations": [
            {"type": "insert", "position": 6, "text": "mut "},
            {"type": "delete", "start": 0, "length": 6},
        ],
    }
    algo = CodeEnginePieceTableAlgo()
    res = algo.execute(payload)
    assert res["algorithm"] == "ALGO-BUF-141"
    assert res["text"] == "mut x = 10;"


def test_line_index_operations():
    code = "line 1\nline 2\nline 3"
    algo = CodeEngineLineIndexAlgo()
    res = algo.execute({"text": code, "queries": [{"offset": 7}]})
    assert res["algorithm"] == "ALGO-BUF-142"
    assert res["query_results"][0]["line"] == 2


def test_undo_redo_stack_operations():
    algo = CodeEngineUndoRedoStackAlgo()
    res = algo.execute({
        "initial_text": "v1",
        "actions": [
            {"type": "edit", "offset": 2, "length": 0, "new_text": " -> v2"},
            {"type": "undo"},
            {"type": "redo"},
        ]
    })
    assert res["algorithm"] == "ALGO-BUF-144"
    assert res["current_text"] == "v1 -> v2"


def test_text_edit_algo():
    algo = CodeEngineTextEditAlgo()
    res = algo.execute({
        "text": "Hello World",
        "start_offset": 6,
        "end_offset": 11,
        "new_text": "Universe",
    })
    assert res["algorithm"] == "ALGO-BUF-117"
    assert res["result_text"] == "Hello Universe"


def test_workspace_edit_algo():
    algo = CodeEngineWorkspaceEditAlgo()
    res = algo.execute({
        "files": {"file1.py": "x = 1\ny = 2\n", "file2.py": "z = 3\n"},
        "changes": {
            "file1.py": [{"start_offset": 4, "end_offset": 5, "new_text": "100"}],
            "file2.py": [{"start_offset": 4, "end_offset": 5, "new_text": "300"}],
        }
    })
    assert res["algorithm"] == "ALGO-BUF-118"
    assert res["updated_files"]["file1.py"] == "x = 100\ny = 2\n"
    assert res["updated_files"]["file2.py"] == "z = 300\n"


def test_position_encoding_algo():
    algo = CodeEnginePositionEncodingAlgo()
    res = algo.execute({"text": "Hello 🚀 World", "query_type": "codepoint", "value": 8})
    assert res["algorithm"] == "ALGO-BUF-119"
    assert res["utf8_bytes"] > 8


def test_reverse_order_application():
    algo = CodeEngineReverseOrderEditAlgo()
    res = algo.execute({
        "text": "A B C D E",
        "edits": [
            {"start_offset": 0, "end_offset": 1, "new_text": "ALPHA"},
            {"start_offset": 8, "end_offset": 9, "new_text": "EPSILON"},
        ]
    })
    assert res["algorithm"] == "ALGO-BUF-120"
    assert res["result_text"] == "ALPHA B C D EPSILON"
    assert res["is_valid"] is True


def test_interval_tree_algo():
    algo = CodeEngineIntervalTreeAlgo()
    res = algo.execute({
        "intervals": [
            {"start": 10, "end": 20, "data": "edit1"},
            {"start": 30, "end": 40, "data": "edit2"},
        ],
        "query_range": {"start": 15, "end": 25},
    })
    assert res["algorithm"] == "ALGO-BUF-122"
    assert res["has_overlap"] is True
    assert res["overlapping_count"] == 1


def test_edit_rebasing_algo():
    algo = CodeEngineEditRebasingAlgo()
    res = algo.execute({
        "prior_edit": {"start_offset": 5, "end_offset": 10, "new_text": "12345678"},
        "target_edit": {"start_offset": 20, "end_offset": 25},
    })
    assert res["algorithm"] == "ALGO-BUF-123"
    assert res["rebased_start"] == 23
    assert res["has_conflict"] is False


def test_idempotent_edits_algo():
    algo = CodeEngineIdempotentEditsAlgo()
    res = algo.execute({
        "document_text": "int a = 1; int b = 2;",
        "search_pattern": "int ",
        "replacement": "let ",
    })
    assert res["algorithm"] == "ALGO-BUF-126"
    assert res["is_idempotent"] is True
