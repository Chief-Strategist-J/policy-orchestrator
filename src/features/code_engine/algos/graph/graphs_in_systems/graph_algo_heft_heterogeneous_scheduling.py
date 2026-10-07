"""ALGORITHM & ARCHITECTURE BLUEPRINT: HETEROGENEOUS EARLIEST FINISH TIME (HEFT) (ALGO-GRAPH-SYS-304)

1. OVERVIEW & OBJECTIVE
HEFT (Topcuoglu, Hariri, Wu) is a static list-scheduling heuristic that assigns tasks with precedence constraints
and communication costs onto a heterogeneous distributed computing environment (mixed CPU/GPU processors with varied speeds).
Computes upward ranks rank_u(t) based on mean execution and communication costs, sorts tasks in descending rank order,
and schedules each task onto the processor that minimizes the Earliest Finish Time (EFT) using an insertion-based idle slot policy.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * |Processors| + |E|) processor schedule tables and edge communication weights.
- Time Complexity: O(|V|^2 * |Processors|) task rank computation and insertion search.
- Invariants:
  - Task execution strictly begins only after all predecessor outputs are transmitted and ready.
  - Non-preemptive execution: task runs uninterrupted on assigned processor from AST to AFT.

3. INPUT PARAMETERS:
- precedence_dag: Mapping[TNode, Collection[TNode]] task precedence dependencies.
- computation_costs: Mapping[TNode, Mapping[str, float]] execution time of task t on processor p: w_{i, j}.
- communication_costs: Mapping[tuple[TNode, TNode], float] data transfer penalty c_{i, k} between tasks on different processors.
- processors: Sequence[str] set of available heterogeneous processors / worker nodes.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'schedule': Dict[TNode, Dict[str, Any]] task assignment details: 'processor', 'start_time', 'finish_time'.
  - 'makespan': float overall workflow completion time max_{u} AFT(u).
  - 'processor_timelines': Dict[str, List[tuple[TNode, float, float]]] chronological task slots per processor.
  - 'upward_ranks': Dict[TNode, float] calculated upward priority ranks.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic task typing via `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHeftHeterogeneousScheduling(Generic[TNode]):
    """Heterogeneous Earliest Finish Time (HEFT) list scheduler with insertion-based slot filling.

    ```yaml
    contract:
      id: ALGO-GRAPH-SYS-304
      name: GraphAlgoHeftHeterogeneousScheduling
      inputs:
        - name: precedence_dag
          type: Mapping[TNode, Collection[TNode]]
          description: DAG of task precedence constraints.
        - name: computation_costs
          type: Mapping[TNode, Mapping[str, float]]
          description: Cost matrix w(task, proc).
        - name: processors
          type: Sequence[str]
          description: List of processor/worker identifiers.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Task-to-processor schedule, total makespan, and processor timelines.
      parameters:
        communication_costs: Optional[Mapping[tuple[TNode, TNode], float]] (default None)
      capability_tags:
        - SCHEDULING
        - HEFT
        - HETEROGENEOUS_COMPUTING
        - WORKFLOW_PLACEMENT
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V|^2 * |P|)
        space: O(|V| * |P| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        precedence_dag: Mapping[TNode, Collection[TNode]],
        computation_costs: Mapping[TNode, Mapping[str, float]],
        processors: Sequence[str],
        communication_costs: Optional[Mapping[Tuple[TNode, TNode], float]] = None,
    ) -> Dict[str, Any]:
        """Runs upward rank calculation and insertion-based EFT scheduling."""
        proc_list = list(processors)
        num_p = len(proc_list)
        all_nodes = list(computation_costs.keys())
        if not all_nodes or num_p == 0:
            return {
                "schedule": {},
                "makespan": 0.0,
                "processor_timelines": {p: [] for p in proc_list},
                "upward_ranks": {},
            }

        comm = communication_costs if communication_costs is not None else {}

        succ_map: Dict[TNode, Set[TNode]] = {u: set(precedence_dag.get(u, [])) for u in all_nodes}
        pred_map: Dict[TNode, Set[TNode]] = {u: set() for u in all_nodes}
        for u, succs in succ_map.items():
            for v in succs:
                if v in pred_map:
                    pred_map[v].add(u)

        avg_comp: Dict[TNode, float] = {}
        for u in all_nodes:
            costs = [computation_costs[u].get(p, 1.0) for p in proc_list]
            avg_comp[u] = sum(costs) / float(num_p)

        upward_ranks: Dict[TNode, float] = {}

        def get_rank(u: TNode) -> float:
            if u in upward_ranks:
                return upward_ranks[u]
            if not succ_map[u]:
                val = avg_comp[u]
            else:
                max_succ = max(
                    comm.get((u, v), 0.0) + get_rank(v) for v in succ_map[u]
                )
                val = avg_comp[u] + max_succ
            upward_ranks[u] = val
            return val

        for u in all_nodes:
            get_rank(u)

        sorted_tasks = sorted(all_nodes, key=lambda u: upward_ranks[u], reverse=True)

        proc_schedules: Dict[str, List[Tuple[TNode, float, float]]] = {p: [] for p in proc_list}
        task_schedule: Dict[TNode, Dict[str, Any]] = {}

        for u in sorted_tasks:
            best_proc = proc_list[0]
            best_ast = 1e18
            best_aft = 1e18

            for p in proc_list:
                comp_time = computation_costs[u].get(p, 1.0)

                ready_time = 0.0
                for pred in pred_map[u]:
                    pred_info = task_schedule[pred]
                    pred_proc = pred_info["processor"]
                    pred_aft = pred_info["finish_time"]
                    transfer_c = comm.get((pred, u), 0.0) if pred_proc != p else 0.0
                    ready_time = max(ready_time, pred_aft + transfer_c)

                ast, aft = self._find_earliest_slot(proc_schedules[p], ready_time, comp_time)
                if aft < best_aft:
                    best_aft = aft
                    best_ast = ast
                    best_proc = p

            task_schedule[u] = {
                "processor": best_proc,
                "start_time": best_ast,
                "finish_time": best_aft,
                "computation_cost": computation_costs[u].get(best_proc, 1.0),
            }

            proc_schedules[best_proc].append((u, best_ast, best_aft))
            proc_schedules[best_proc].sort(key=lambda slot: slot[1])

        makespan = max((t["finish_time"] for t in task_schedule.values()), default=0.0)

        return {
            "schedule": task_schedule,
            "makespan": makespan,
            "processor_timelines": proc_schedules,
            "upward_ranks": upward_ranks,
        }

    def _find_earliest_slot(
        self,
        timeline: List[Tuple[TNode, float, float]],
        ready_time: float,
        duration: float,
    ) -> Tuple[float, float]:
        """Finds insertion slot on processor timeline minimizing finish time."""
        if not timeline:
            return ready_time, ready_time + duration

        if ready_time + duration <= timeline[0][1]:
            return ready_time, ready_time + duration

        for i in range(len(timeline) - 1):
            gap_start = max(ready_time, timeline[i][2])
            gap_end = timeline[i + 1][1]
            if gap_end - gap_start >= duration:
                return gap_start, gap_start + duration

        last_finish = max(ready_time, timeline[-1][2])
        return last_finish, last_finish + duration
