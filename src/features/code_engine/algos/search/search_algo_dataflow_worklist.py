"""
================================================================================
ALGORITHM BLUEPRINT: DATAFLOW ANALYSIS WORKLIST ITERATION ENGINE
================================================================================

1. OVERVIEW:
   Implements a generic Dataflow Analysis Worklist Framework computing program
   properties across basic blocks. Evaluates monotonic property lattices (e.g.
   Reaching Definitions, Liveness, Available Expressions) using transfer functions:
   OUT[B] = GEN[B] U (IN[B] - KILL[B]). Iterates until reaching a mathematical fixpoint.

2. WORKLIST ALGORITHM PIPELINE:
   - Initialization: Set IN[B] = OUT[B] = empty set for all blocks B; populate worklist.
   - Iteration:
       1. Pop block B from worklist queue.
       2. IN[B] = Join_{P in Pred(B)} (OUT[P]) (Union or Intersection).
       3. New_OUT = Transfer(B, IN[B]) = GEN[B] U (IN[B] - KILL[B]).
       4. If New_OUT != OUT[B]:
           OUT[B] = New_OUT
           Push all successors Succ(B) onto worklist.
   - Termination: Monotonic growth on finite height lattice guarantees termination.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(B * H) where B is block count and H is lattice height.
   - Correctness: Guaranteed exact least/greatest fixpoint.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import deque
from typing import Dict, List, Any, Optional, Set, Tuple


class SearchEngineDataflowWorklistAlgo:
    """
    Implements generic worklist-based dataflow analysis over CFG basic blocks.
    """

    def solve_reaching_definitions(
        self,
        blocks_data: List[Dict[str, Any]],
        successors_map: Dict[int, List[int]],
        predecessors_map: Dict[int, List[int]]
    ) -> Dict[str, Any]:
        """
        Solves reaching definitions across blocks using GEN/KILL sets.
        """
        gen_map: Dict[int, Set[str]] = {}
        kill_map: Dict[int, Set[str]] = {}
        in_map: Dict[int, Set[str]] = {}
        out_map: Dict[int, Set[str]] = {}

        block_ids: List[int] = []
        for b in blocks_data:
            b_id = int(b["id"])
            block_ids.append(b_id)
            gen_map[b_id] = set(b.get("gen", []))
            kill_map[b_id] = set(b.get("kill", []))
            in_map[b_id] = set()
            out_map[b_id] = set()

        worklist = deque(block_ids)
        iterations = 0

        while worklist and iterations < 1000:
            iterations += 1
            b_id = worklist.popleft()

            preds = predecessors_map.get(b_id, [])
            new_in: Set[str] = set()
            for p in preds:
                new_in |= out_map.get(p, set())
            in_map[b_id] = new_in

            new_out = gen_map[b_id] | (in_map[b_id] - kill_map[b_id])

            if new_out != out_map[b_id]:
                out_map[b_id] = new_out
                for succ in successors_map.get(b_id, []):
                    if succ not in worklist:
                        worklist.append(succ)

        return {
            "iterations_to_fixpoint": iterations,
            "block_facts": [
                {
                    "block_id": b_id,
                    "in_facts": sorted(list(in_map[b_id])),
                    "out_facts": sorted(list(out_map[b_id]))
                } for b_id in block_ids
            ]
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes dataflow worklist analysis over provided block GEN/KILL sets and topology.
        """
        blocks = payload.get("blocks", [])
        raw_succs = payload.get("successors", {})
        raw_preds = payload.get("predecessors", {})

        succ_map: Dict[int, List[int]] = {int(k): [int(x) for x in v] for k, v in raw_succs.items()}
        pred_map: Dict[int, List[int]] = {int(k): [int(x) for x in v] for k, v in raw_preds.items()}

        result = self.solve_reaching_definitions(blocks, succ_map, pred_map)

        return {
            "algorithm": "ALGO-SRCH-96",
            "dataflow_result": result
        }
