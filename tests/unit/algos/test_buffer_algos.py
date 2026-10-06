"""
================================================================================
UNIT TESTS: CODE ENGINE BUFFER ALGORITHMS (PART 3)
================================================================================

Tests deterministic execution for:
- Gap Buffer (ALGO-BUF-139)
- Rope (ALGO-BUF-140)
- Piece Table (ALGO-BUF-141)
- Line Index (ALGO-BUF-142)
- Undo/Redo Stack (ALGO-BUF-144)
================================================================================
"""

import pytest
from src.features.code_engine.algos.buffer import (
    CodeEngineGapBufferAlgo,
    CodeEngineRopeAlgo,
    CodeEnginePieceTableAlgo,
    CodeEngineLineIndexAlgo,
    CodeEngineUndoRedoStackAlgo,
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
    assert res["length"] == len(">>> Hello Beautiful World")


def test_gap_buffer_deletion():
    payload = {
        "initial_text": "abcdef",
        "gap_size": 4,
        "operations": [
            {"type": "move", "position": 3},
            {"type": "delete_backward", "count": 1},
            {"type": "delete_forward", "count": 1},
        ],
    }
    algo = CodeEngineGapBufferAlgo()
    res = algo.execute(payload)
    assert res["text"] == "abef"


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
    assert not res["text"].startswith("The ")


def test_piece_table_operations():
    payload = {
        "initial_text": "const x = 10;",
        "operations": [
            {"type": "insert", "position": 6, "text": "mut "},
            {"type": "insert", "position": 18, "text": " // set value"},
            {"type": "delete", "start": 0, "length": 6},
        ],
    }
    algo = CodeEnginePieceTableAlgo()
    res = algo.execute(payload)
    assert res["algorithm"] == "ALGO-BUF-141"
    assert res["text"] == "mut x = 10; // set value"
    assert res["total_pieces"] >= 2


def test_line_index_operations():
    code = "line 1\nline 2 with more text\r\nline 3\nline 4"
    payload = {
        "text": code,
        "queries": [
            {"offset": 0},
            {"offset": 7},
            {"line": 2, "column": 8},
            {"line": 4, "column": 1},
        ],
    }
    algo = CodeEngineLineIndexAlgo()
    res = algo.execute(payload)
    assert res["algorithm"] == "ALGO-BUF-142"
    assert res["total_lines"] == 4
    results = res["query_results"]
    assert results[0]["line"] == 1
    assert results[0]["column"] == 1
    assert results[1]["line"] == 2
    assert results[1]["column"] == 1


def test_undo_redo_stack_operations():
    payload = {
        "initial_text": "version 1",
        "max_history": 50,
        "actions": [
            {"type": "edit", "offset": 9, "length": 0, "new_text": " -> version 2", "description": "add v2"},
            {"type": "edit", "offset": 22, "length": 0, "new_text": " -> version 3", "description": "add v3"},
            {"type": "undo"},
            {"type": "redo"},
            {"type": "undo"},
        ],
    }
    algo = CodeEngineUndoRedoStackAlgo()
    res = algo.execute(payload)
    assert res["algorithm"] == "ALGO-BUF-144"
    assert res["current_text"] == "version 1 -> version 2"
    assert res["can_undo"] is True
    assert res["can_redo"] is True
