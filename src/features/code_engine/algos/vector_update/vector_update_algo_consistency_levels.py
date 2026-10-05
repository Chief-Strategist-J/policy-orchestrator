"""
================================================================================
ALGORITHM BLUEPRINT: CONSISTENCY LEVELS AND READ-YOUR-WRITES (ALGO-VEC-UPD-134)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates read-consistency requirements against replica status. Handles
   EVENTUAL, READ_YOUR_WRITES, BOUNDED_STALENESS, and STRONG consistency checks.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoConsistencyLevels:
    """
    --- contract:
      id: ALGO-VEC-UPD-134
      name: VectorUpdateAlgoConsistencyLevels
      category: update
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        consistency_level: str
        replica_sequence_num: int
        client_write_token_seq: Optional[int]
        max_staleness_allowed: int
        leader_sequence_num: int
      output_schema:
        is_read_permitted: bool
        required_wait_seq_diff: int
        effective_level: str
    ---
    """

    @classmethod
    def check_read_eligibility(
        cls,
        consistency_level: str = "READ_YOUR_WRITES",
        replica_sequence_num: int = 100,
        client_write_token_seq: Optional[int] = None,
        max_staleness_allowed: int = 5,
        leader_sequence_num: int = 105,
    ) -> Dict[str, Any]:
        level = consistency_level.upper()
        permitted = True
        diff = 0

        if level == "STRONG":
            diff = max(0, leader_sequence_num - replica_sequence_num)
            permitted = (diff == 0)
        elif level == "READ_YOUR_WRITES":
            req = client_write_token_seq or 0
            diff = max(0, req - replica_sequence_num)
            permitted = (diff == 0)
        elif level == "BOUNDED_STALENESS":
            lag = max(0, leader_sequence_num - replica_sequence_num)
            diff = max(0, lag - max_staleness_allowed)
            permitted = (lag <= max_staleness_allowed)
        elif level == "EVENTUAL":
            permitted = True
            diff = 0

        return {
            "is_read_permitted": permitted,
            "required_wait_seq_diff": diff,
            "effective_level": level,
        }
