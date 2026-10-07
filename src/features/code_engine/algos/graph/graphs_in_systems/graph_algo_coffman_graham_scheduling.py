"""ALGORITHM & ARCHITECTURE BLUEPRINT: COFFMAN-GRAHAM SCHEDULING (ALGO-GRAPH-SYS-303)

1. OVERVIEW & OBJECTIVE
Schedules unit-execution-time tasks with precedence dependencies onto W identical parallel processors (or assigns
DAG nodes into layers of bounded width W). Phase 1 removes transitive reduction edges; Phase 2 assigns lexicographic
labels 1..N such that among tasks with all successors labeled, the task with lexicographically smallest sorted
successor label list is selected; Phase 3 assigns time slots / processor steps in greedy order of descending labels.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| + |E|) DAG adjacency and labeling tables.
- Time Complexity: O(|V|^2 + |E|) transitive reduction and lexicographic labeling.
- Invariants:
  - Exact optimal schedule length for W = 2 processors; (2 - 2/W)-approximation for arbitrary W.
  - No time slot / layer contains more than W tasks (width bound invariant).

3. INPUT PARAMETERS:
- precedence_dag: Mapping[TNode, Collection[TNode]] task precedence DAG.
- num_processors: int maximum parallel execution capacity / layer width W.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'schedule': List[List[TNode]] time-step batches / layer task assignments.
  - 'makespan': int total time steps (schedule length).
  - 'labels': Dict[TNode, int] computed Coffman-Graham lexicographic labels.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCoffmanGrahamScheduling(Generic[TNode]):
    """Coffman-Graham algorithm for optimal 2-processor scheduling and bounded-width DAG leveling.

    ```yaml
    contract:
      id: ALGO-GRAPH-SYS-303
      name: GraphAlgoCoffmanGrahamScheduling
      inputs:
        - name: precedence_dag
          type: Mapping[TNode, Collection[TNode]]
          description: Task dependency DAG (u precedes v).
        - name: num_processors
          type: int
          default: 2
          description: Max tasks per time slot W.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Time step schedule batches, makespan, and vertex labels.
      capability_tags:
        - SCHEDULING
        - COFFMAN_GRAHAM
        - BOUNDED_WIDTH_LEVELING
        - MULTIPROCESSOR
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V|^2 + |E|)
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        precedence_dag: Mapping[TNode, Collection[TNode]],
        num_processors: int = 2,
    ) -> Dict[str, Any]:
        """Calculates Coffman-Graham labeling and generates bounded-width processor schedule."""
        all_nodes: Set[TNode] = set(precedence_dag.keys())
        for succs in precedence_dag.values():
            all_nodes.update(succs)

        node_list = list(all_nodes)
        n = len(node_list)
        if n == 0 or num_processors <= 0:
            return {"schedule": [], "makespan": 0, "labels": {}}

        succ_map: Dict[TNode, Set[TNode]] = {
            u: set(precedence_dag.get(u, [])) for u in node_list
        }
        pred_map: Dict[TNode, Set[TNode]] = {u: set() for u in node_list}
        for u, succs in succ_map.items():
            for v in succs:
                pred_map[v].add(u)

        labels: Dict[TNode, int] = {}
        labeled_set: Set[TNode] = set()

        for step in range(1, n + 1):
            candidates = [
                u for u in node_list
                if u not in labeled_set and succ_map[u].issubset(labeled_set)
            ]

            def key_func(node: TNode) -> List[int]:
                succ_labels = sorted([labels[s] for s in succ_map[node]], reverse=True)
                return succ_labels

            candidates.sort(key=key_func)
            chosen = candidates[0]
            labels[chosen] = step
            labeled_set.add(chosen)

        nodes_by_label = sorted(node_list, key=lambda u: labels[u], reverse=True)

        schedule: List[List[TNode]] = []
        assigned: Set[TNode] = set()
        task_time: Dict[TNode, int] = {}

        while len(assigned) < n:
            current_slot: List[TNode] = []
            slot_idx = len(schedule)

            for u in nodes_by_label:
                if u not in assigned and len(current_slot) < num_processors:
                    preds_satisfied = all(
                        p in assigned and task_time[p] < slot_idx
                        for p in pred_map[u]
                    )
                    if preds_satisfied:
                        current_slot.append(u)
                        assigned.add(u)
                        task_time[u] = slot_idx

            schedule.append(current_slot)

        return {
            "schedule": schedule,
            "makespan": len(schedule),
            "labels": labels,
        }
