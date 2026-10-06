"""
================================================================================
UNIT TESTS: CODE ENGINE ATOMIC MUTATION ALGORITHMS (PART 4)
================================================================================
"""

import pytest
from src.features.code_engine.algos.atomic_mutation import (
    CodeEngineDryRunPlannerAlgo,
    CodeEngineCasContentHashAlgo,
    CodeEngineWriteAheadJournalAlgo,
    CodeEngineSagaCompensatorAlgo,
    CodeEngineFileIdentityPreserverAlgo,
    CodeEnginePostConditionSearchAlgo,
    CodeEngineExactReplaceUniqueAlgo,
)


def test_dry_run_planner():
    files = {"src/app.py": "def main():\n    pass\n"}
    edits = [{"file_path": "src/app.py", "action": "modify", "search_text": "pass", "replace_text": "return 0"}]
    algo = CodeEngineDryRunPlannerAlgo()
    res = algo.execute({"files": files, "planned_edits": edits})
    assert res["algorithm"] == "ALGO-ATMC-157"
    assert res["can_apply"] is True
    assert res["plan_summary"]["affected_files"] == 1


def test_cas_content_hash():
    algo = CodeEngineCasContentHashAlgo()
    content = "stable content"
    h = algo.compute_sha256(content)
    res = algo.execute({
        "current_content": content,
        "expected_sha256": h,
        "new_content": "updated content",
    })
    assert res["algorithm"] == "ALGO-ATMC-159"
    assert res["cas_success"] is True
    assert res["result_content"] == "updated content"


def test_write_ahead_journal():
    files = {"a.py": "original_a", "b.py": "original_b"}
    mutations = {"a.py": "new_a", "b.py": "new_b"}
    algo = CodeEngineWriteAheadJournalAlgo()
    res_apply = algo.execute({"files": files, "mutations": mutations, "action": "apply"})
    assert res_apply["algorithm"] == "ALGO-ATMC-161"
    assert res_apply["status"] == "applied"

    res_rollback = algo.execute({
        "files": res_apply["restored_files"],
        "pre_images": files,
        "action": "rollback",
    })
    assert res_rollback["status"] == "rolled_back"
    assert res_rollback["restored_files"]["a.py"] == "original_a"


def test_saga_compensator():
    steps = [
        {"name": "step1_git_branch", "forward": "create", "compensate": "delete"},
        {"name": "step2_write_files", "forward": "write", "compensate": "restore"},
        {"name": "step3_run_linter", "forward": "lint", "compensate": "none"},
    ]
    algo = CodeEngineSagaCompensatorAlgo()
    res_fail = algo.execute({"steps": steps, "fail_at_step": "step3_run_linter"})
    assert res_fail["algorithm"] == "ALGO-ATMC-163"
    assert res_fail["overall_status"] == "compensated_failure"
    assert "step2_write_files" in res_fail["compensated_steps"]


def test_file_identity_preserver():
    text = "line 1\r\nline 2\r\n"
    algo = CodeEngineFileIdentityPreserverAlgo()
    res = algo.execute({"raw_bytes_hex": text.encode("utf-8").hex(), "modified_text": "line 1\nline 2 modified\n"})
    assert res["algorithm"] == "ALGO-ATMC-165"
    assert res["detected_crlf"] is True
    assert "\r\n" in res["reconstructed_text"]


def test_postcondition_search():
    files = {
        "src/a.py": "def foo():\n    return 1\n",
        "src/b.py": "def bar():\n    legacy_marker()\n",
    }
    algo = CodeEnginePostConditionSearchAlgo()
    res = algo.execute({"files": files, "deprecated_pattern": "legacy_marker"})
    assert res["algorithm"] == "ALGO-ATMC-184"
    assert res["zero_remaining"] is False
    assert res["remaining_count"] == 1


def test_exact_replace_unique():
    doc = "alpha beta gamma delta"
    algo = CodeEngineExactReplaceUniqueAlgo()
    res = algo.execute({
        "document_text": doc,
        "target_string": "beta",
        "replacement_string": "BETA_MODIFIED",
    })
    assert res["algorithm"] == "ALGO-ATMC-195"
    assert res["is_success"] is True
    assert "BETA_MODIFIED" in res["updated_text"]
