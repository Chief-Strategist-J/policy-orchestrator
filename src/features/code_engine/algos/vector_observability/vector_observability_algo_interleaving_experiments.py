"""
================================================================================
ALGORITHM BLUEPRINT: TEAM-DRAFT INTERLEAVING EXPERIMENTS (ALGO-VEC-OBS-166)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Merges two candidate ranking lists (Ranker A vs Ranker B) into a single unbiased
   interleaved stream and attributes user preference clicks with statistical win rates.

2. MATHEMATICAL FORMULATION:
   Team-Draft Interleaving: Alternates assigning top available unassigned items
   to Team A and Team B based on coin-flip priority.
   Win Margin = (Clicks_A - Clicks_B) / (Clicks_A + Clicks_B)
================================================================================
"""

import random
from typing import Any, Dict, List, Optional, Tuple


class VectorObservabilityAlgoInterleavingExperiments:
    """
    --- contract:
      id: ALGO-VEC-OBS-166
      name: VectorObservabilityAlgoInterleavingExperiments
      category: observability
      complexity: O(k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        ranker_a_results: list[str]
        ranker_b_results: list[str]
        k: int
        seed: Optional[int]
        clicked_ids: Optional[list[str]]
      output_schema:
        interleaved_list: list[str]
        item_assignments: dict[str, str]
        ranker_a_clicks: int
        ranker_b_clicks: int
        winning_ranker: Optional[str]
    ---
    """

    @classmethod
    def interleave_and_score(
        cls,
        ranker_a_results: List[str],
        ranker_b_results: List[str],
        k: int = 10,
        seed: Optional[int] = None,
        clicked_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        rng = random.Random(seed if seed is not None else 42)
        interleaved: List[str] = []
        assignments: Dict[str, str] = {}

        idx_a = 0
        idx_b = 0
        len_a = len(ranker_a_results)
        len_b = len(ranker_b_results)
        chosen_set = set()

        team_a_count = 0
        team_b_count = 0

        while len(interleaved) < k and (idx_a < len_a or idx_b < len_b):
            turn = "A" if team_a_count < team_b_count else ("B" if team_b_count < team_a_count else ("A" if rng.random() < 0.5 else "B"))

            if turn == "A":
                while idx_a < len_a and ranker_a_results[idx_a] in chosen_set:
                    idx_a += 1
                if idx_a < len_a:
                    item = ranker_a_results[idx_a]
                    interleaved.append(item)
                    chosen_set.add(item)
                    assignments[item] = "A"
                    team_a_count += 1
                    idx_a += 1
                else:
                    team_a_count += 1
            else:
                while idx_b < len_b and ranker_b_results[idx_b] in chosen_set:
                    idx_b += 1
                if idx_b < len_b:
                    item = ranker_b_results[idx_b]
                    interleaved.append(item)
                    chosen_set.add(item)
                    assignments[item] = "B"
                    team_b_count += 1
                    idx_b += 1
                else:
                    team_b_count += 1

        clicks_a = 0
        clicks_b = 0
        if clicked_ids:
            for cid in clicked_ids:
                team = assignments.get(cid)
                if team == "A":
                    clicks_a += 1
                elif team == "B":
                    clicks_b += 1

        winning: Optional[str] = None
        if clicked_ids:
            if clicks_a > clicks_b:
                winning = "A"
            elif clicks_b > clicks_a:
                winning = "B"
            else:
                winning = "TIE"

        return {
            "interleaved_list": interleaved,
            "item_assignments": assignments,
            "ranker_a_clicks": clicks_a,
            "ranker_b_clicks": clicks_b,
            "winning_ranker": winning,
        }
