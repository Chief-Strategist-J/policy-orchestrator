"""ALGORITHM & ARCHITECTURE BLUEPRINT: CRITICAL PATH METHOD (CPM) AND PERT (ALGO-GRAPH-SYS-302)

1. OVERVIEW & OBJECTIVE
Finds the longest dependency chain (Critical Path) in project/workflow DAGs and computes Earliest Start (ES),
Earliest Finish (EF), Latest Start (LS), Latest Finish (LF), and Total/Free Float (Slack) per activity.
Under Program Evaluation and Review Technique (PERT), estimates expected duration mu = (o + 4m + p)/6 and variance
sigma^2 = ((p - o)/6)^2 from three-point (optimistic, most likely, pessimistic) activity distributions.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| + |E|) DAG representation and schedule tables.
- Time Complexity: O(|V| + |E|) forward and backward topological passes.
- Invariants:
  - Critical path activities possess exactly zero total slack: LS(u) - ES(u) == 0.
  - Total project duration equals max_{u} EF(u).

3. INPUT PARAMETERS:
- dependency_dag: Mapping[TNode, Collection[TNode]] task dependency DAG (u -> v meaning u must finish before v starts).
- durations: Mapping[TNode, float | tuple[float, float, float]] task durations (scalar float for CPM, or (optimistic, most_likely, pessimistic) tuple for PERT).

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'critical_path': List[TNode] sequence of zero-slack tasks governing total project duration.
  - 'project_duration': float minimum total completion time.
  - 'schedule_table': Dict[TNode, Dict[str, float]] activity timing table containing 'ES', 'EF', 'LS', 'LF', 'slack'.
  - 'pert_variance': float variance of project duration under PERT model.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic task typing via `TNode`.
"""

from __future__ import annotations

import collections
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar, Union

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCriticalPathPert(Generic[TNode]):
    """Critical Path Method (CPM) and PERT schedule analyzer for dependency DAGs.

    ```yaml
    contract:
      id: ALGO-GRAPH-SYS-302
      name: GraphAlgoCriticalPathPert
      inputs:
        - name: dependency_dag
          type: Mapping[TNode, Collection[TNode]]
          description: Precedence DAG where edge u -> v denotes u precedes v.
        - name: durations
          type: Mapping[TNode, Union[float, tuple[float, float, float]]]
          description: Task durations (scalar float or (opt, most_likely, pess) 3-tuple).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Critical path tasks, total duration, PERT variance, and activity schedule.
      capability_tags:
        - SCHEDULING
        - CPM
        - PERT
        - CRITICAL_PATH
        - WORKFLOW_OPTIMIZATION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V| + |E|)
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        dependency_dag: Mapping[TNode, Collection[TNode]],
        durations: Mapping[TNode, Union[float, Tuple[float, float, float]]],
    ) -> Dict[str, Any]:
        """Performs forward/backward passes to compute critical path and slack."""
        all_nodes: Set[TNode] = set(dependency_dag.keys())
        for successors_coll in dependency_dag.values():
            all_nodes.update(successors_coll)
        all_nodes.update(durations.keys())

        node_list = list(all_nodes)
        if not node_list:
            return {
                "critical_path": [],
                "project_duration": 0.0,
                "schedule_table": {},
                "pert_variance": 0.0,
            }

        task_duration: Dict[TNode, float] = {}
        task_variance: Dict[TNode, float] = {}

        for u in node_list:
            d_spec = durations.get(u, 0.0)
            if isinstance(d_spec, (tuple, list)) and len(d_spec) == 3:
                o, m, p = float(d_spec[0]), float(d_spec[1]), float(d_spec[2])
                exp_d = (o + 4.0 * m + p) / 6.0
                var_d = ((p - o) / 6.0) ** 2
                task_duration[u] = max(0.0, exp_d)
                task_variance[u] = max(0.0, var_d)
            else:
                task_duration[u] = max(0.0, float(d_spec))
                task_variance[u] = 0.0

        preds: Dict[TNode, Set[TNode]] = {u: set() for u in node_list}
        succs: Dict[TNode, Set[TNode]] = {u: set() for u in node_list}

        for u, nbrs in dependency_dag.items():
            for v in nbrs:
                if v in succs:
                    succs[u].add(v)
                    preds[v].add(u)

        in_deg = {u: len(preds[u]) for u in node_list}
        queue = collections.deque([u for u in node_list if in_deg[u] == 0])
        topo_order: List[TNode] = []

        while queue:
            curr = queue.popleft()
            topo_order.append(curr)
            for v in succs[curr]:
                in_deg[v] -= 1
                if in_deg[v] == 0:
                    queue.append(v)

        es: Dict[TNode, float] = {u: 0.0 for u in node_list}
        ef: Dict[TNode, float] = {u: 0.0 for u in node_list}

        for u in topo_order:
            max_pred_ef = max((ef[p] for p in preds[u]), default=0.0)
            es[u] = max_pred_ef
            ef[u] = es[u] + task_duration[u]

        total_duration = max((ef[u] for u in node_list), default=0.0)

        lf: Dict[TNode, float] = {u: total_duration for u in node_list}
        ls: Dict[TNode, float] = {u: total_duration for u in node_list}

        for u in reversed(topo_order):
            if succs[u]:
                min_succ_ls = min(ls[s] for s in succs[u])
                lf[u] = min_succ_ls
            else:
                lf[u] = total_duration
            ls[u] = lf[u] - task_duration[u]

        schedule: Dict[TNode, Dict[str, float]] = {}
        critical_nodes: Set[TNode] = set()

        for u in node_list:
            slack_val = ls[u] - es[u]
            schedule[u] = {
                "ES": es[u],
                "EF": ef[u],
                "LS": ls[u],
                "LF": lf[u],
                "slack": slack_val,
                "duration": task_duration[u],
            }
            if abs(slack_val) < 1e-6:
                critical_nodes.add(u)

        critical_path: List[TNode] = []
        curr_candidates = [u for u in topo_order if u in critical_nodes and len(preds[u]) == 0]
        if not curr_candidates:
            curr_candidates = [u for u in topo_order if u in critical_nodes]

        if curr_candidates:
            curr_candidates.sort(key=lambda u: es[u])
            curr = curr_candidates[0]
            critical_path.append(curr)

            while True:
                next_cands = [v for v in succs[curr] if v in critical_nodes]
                if not next_cands:
                    break
                next_cands.sort(key=lambda v: es[v])
                curr = next_cands[0]
                critical_path.append(curr)

        pert_variance = sum(task_variance[u] for u in critical_path)

        return {
            "critical_path": critical_path,
            "project_duration": total_duration,
            "schedule_table": schedule,
            "pert_variance": pert_variance,
        }
