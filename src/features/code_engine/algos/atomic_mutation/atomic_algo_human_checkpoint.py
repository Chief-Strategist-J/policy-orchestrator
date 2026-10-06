"""
================================================================================
ALGORITHM BLUEPRINT: HUMAN-IN-THE-LOOP CHECKPOINTS (INTERACTIVE DECISION GATING)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Defines formal interactive approval checkpoints before irreversible actions,
   canary rollouts, or high-blast-radius transformations. Generates concise,
   decision-ready summaries showing top-N representative diffs, affected file counts,
   risk scores, and valid action options (Approve, Reject, Modify Plan). Blocks
   execution until explicit human authorization is recorded.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Non-Presumption of Approval: Timeouts or silent states MUST NEVER be treated
     as implicit approvals.
   - Decision-Ready Summaries: Capped to top representative diff samples (default 3)
     to prevent human cognitive overload.
   - Audit Trail: Records timestamp, approver ID, and rationale for all decisions.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Diff_Samples_Count)
   - Space Complexity: O(Summary_Size)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import time
from typing import Dict, Any, List, Optional


class CodeEngineHumanCheckpointAlgo:
    """
    --- contract:
      id: ALGO-ATMC-205
      name: CodeEngineHumanCheckpointAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(S)
        space: O(S)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - human_in_the_loop.checkpoint
      - decision_gating
      - audit_log
      input_schema:
        checkpoint_name: string
        planned_changes: object
        risk_score: number
      output_schema:
        algorithm: string
        checkpoint_id: string
        status: string
        summary: object
        allowed_actions: array
    ---
    """

    def create_checkpoint(
        self,
        checkpoint_name: str,
        affected_files: List[str],
        sample_diffs: Dict[str, str],
        risk_score: float,
        max_samples: int = 3,
    ) -> Dict[str, Any]:
        sampled = dict(list(sample_diffs.items())[:max_samples])
        return {
            "algorithm": "ALGO-ATMC-205",
            "checkpoint_name": checkpoint_name,
            "status": "AWAITING_HUMAN_DECISION",
            "created_at": time.time(),
            "summary": {
                "total_affected_files": len(affected_files),
                "risk_score": risk_score,
                "is_high_risk": risk_score >= 0.75,
                "sample_diffs": sampled,
                "omitted_diff_count": max(0, len(sample_diffs) - len(sampled)),
            },
            "allowed_actions": ["APPROVE", "REJECT", "MODIFY_PLAN"],
            "decision": None,
        }

    def record_decision(
        self,
        checkpoint: Dict[str, Any],
        action: str,
        approver: str,
        rationale: str = "",
    ) -> Dict[str, Any]:
        norm_action = action.upper()
        if norm_action not in ["APPROVE", "REJECT", "MODIFY_PLAN"]:
            raise ValueError(f"Invalid decision action '{action}'")

        updated = dict(checkpoint)
        status_map = {
            "APPROVE": "APPROVED",
            "REJECT": "REJECTED",
            "MODIFY_PLAN": "MODIFICATION_REQUESTED",
        }
        updated["status"] = status_map[norm_action]
        updated["decision"] = {
            "action": norm_action,
            "approver": approver,
            "rationale": rationale,
            "decided_at": time.time(),
        }
        return updated
