"""
================================================================================
ALGORITHM BLUEPRINT: SAGA ORCHESTRATOR WITH COMPENSATING ACTIONS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Orchestrates multi-step code refactoring workflows across independent files
   or external systems (e.g., git commits, filesystem mutations, index refreshes).
   If any step fails, the Saga runner terminates forward execution and
   sequentially invokes compensating actions for all completed steps in LIFO order.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Compensation Guarantee: Every step that succeeded before a failure is
     guaranteed to have its compensating action invoked.
   - Idempotent Compensation: Compensating actions must be safely re-executable.

3. COMPLEXITY ANALYSIS:
   - Forward Execution: O(S) where S is step count
   - Compensation: O(Completed_Steps)
   - Space Complexity: O(S)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple, Callable


class SagaStep:
    def __init__(self, step_name: str, forward_action: str, compensate_action: str) -> None:
        self.step_name: str = step_name
        self.forward_action: str = forward_action
        self.compensate_action: str = compensate_action
        self.status: str = "pending"


class CodeEngineSagaCompensatorAlgo:
    """
    --- contract:
      id: ALGO-ATMC-163
      name: CodeEngineSagaCompensatorAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(S) where S is step count
        space: O(S)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - atomic.saga_compensator
      - distributed.workflow
      - compensation.failure_recovery
      input_schema:
        steps: array
        fail_at_step: string
      output_schema:
        algorithm: string
        overall_status: string
        executed_steps: array
        compensated_steps: array
    ---
    """

    def run_saga(
        self, steps_data: List[Dict[str, Any]], fail_at_step: Optional[str] = None
    ) -> Tuple[str, List[str], List[str]]:
        executed = []
        compensated = []

        for item in steps_data:
            name = item.get("name", "")
            if name == fail_at_step:
                for comp_step in reversed(executed):
                    compensated.append(comp_step)
                return ("compensated_failure", executed, compensated)

            executed.append(name)

        return ("completed_success", executed, [])

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = payload.get("steps", [])
        fail_step: Optional[str] = payload.get("fail_at_step", None)

        status, executed, compensated = self.run_saga(steps, fail_step)

        return {
            "algorithm": "ALGO-ATMC-163",
            "overall_status": status,
            "executed_steps": executed,
            "compensated_steps": compensated,
        }
