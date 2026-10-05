"""
================================================================================
ALGORITHM BLUEPRINT: RAFT CONSENSUS STATE MACHINE (ALGO-VEC-UPD-136)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements Raft consensus protocol logic for vector log commits: manages terms,
   majority vote aggregation for leader election, and committed sequence progression.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoRaftConsensus:
    """
    --- contract:
      id: ALGO-VEC-UPD-136
      name: VectorUpdateAlgoRaftConsensus
      category: update
      complexity: O(Nodes)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        current_term: int
        cluster_size: int
        vote_responses: list[dict[str, Any]]
        log_match_counts: dict[int, int]
        current_commit_index: int
      output_schema:
        election_won: bool
        new_commit_index: int
        term: int
    ---
    """

    @classmethod
    def evaluate(
        cls,
        current_term: int,
        cluster_size: int,
        vote_responses: List[Dict[str, Any]],
        log_match_counts: Optional[Dict[int, int]] = None,
        current_commit_index: int = 0,
    ) -> Dict[str, Any]:
        majority = (cluster_size // 2) + 1
        yes_votes = sum(1 for v in vote_responses if v.get("vote_granted", False) and v.get("term") == current_term)
        won = yes_votes >= majority

        commit_idx = current_commit_index
        if log_match_counts:
            for idx, count in sorted(log_match_counts.items(), key=lambda x: x[0], reverse=True):
                if idx > commit_idx and count >= majority:
                    commit_idx = idx
                    break

        return {
            "election_won": won,
            "new_commit_index": commit_idx,
            "term": current_term,
            "majority_threshold": majority,
            "positive_votes": yes_votes,
        }
