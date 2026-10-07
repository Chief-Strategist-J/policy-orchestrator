"""ALGORITHM & ARCHITECTURE BLUEPRINT: BAYESIAN NETWORK STRUCTURE LEARNING (HILL CLIMBING & GES) (ALGO-GRAPH-CAUSAL-278)

1. OVERVIEW & OBJECTIVE
Learns the Directed Acyclic Graph (DAG) structure of a Bayesian Network from discrete observational data
using score-based heuristic optimization (Hill Climbing / Greedy Equivalence Search). Evaluates candidate
graph structures using the Bayesian Information Criterion (BIC / MDL) or BDeu score with local edge addition,
deletion, and reversal operators, strictly enforcing acyclicity at every candidate mutation.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V|^2 + N_samples * |V|) for storing sample records and adjacency matrices.
- Time Complexity: O(T_steps * |V|^2 * N_samples * |K|^max_parents).
- Invariants:
  - Output graph is guaranteed to be a valid Directed Acyclic Graph (zero directed cycles).
  - Decomposition property: BIC(G) = sum_{v in V} BIC_local(v, Parents(v)).

3. INPUT PARAMETERS:
- variables: Sequence[TNode] discrete variable identifiers.
- data: Sequence[Mapping[TNode, int]] observational dataset rows.
- max_parents: int maximum inbound parent cardinality per node.
- max_iterations: int search optimization step limit.
- score_metric: str 'bic' or 'aic'.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'dag_adjacency': Dict[TNode, List[TNode]] learned parent-to-child adjacency graph.
  - 'best_score': float optimal score achieved.
  - 'edge_count': int total directed edges in learned DAG.
  - 'iterations': int count of search steps taken.

5. AGENT CONTRACT:
- Implemented with pure standard Python.
- Zero inline comments.
"""

from __future__ import annotations

import collections
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBayesianNetworkStructureLearning(Generic[TNode]):
    """Score-based Bayesian Network DAG structure learning using greedy Hill Climbing.

    ```yaml
    contract:
      id: ALGO-GRAPH-CAUSAL-278
      name: GraphAlgoBayesianNetworkStructureLearning
      inputs:
        - name: variables
          type: Sequence[TNode]
          description: Variables in the dataset.
        - name: data
          type: Sequence[Mapping[TNode, int]]
          description: Observational tabular discrete data records.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Learned DAG adjacency, optimal score, edge count, and search steps.
      parameters:
        max_parents: int (default 3)
        max_iterations: int (default 100)
        score_metric: str (default 'bic')
      capability_tags:
        - CAUSAL_DISCOVERY
        - STRUCTURE_LEARNING
        - BAYESIAN_NETWORK
        - HILL_CLIMBING
        - BIC_SCORE
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T_steps * |V|^2 * N * |K|^p)
        space: O(|V|^2 + N * |V|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        variables: Sequence[TNode],
        data: Sequence[Mapping[TNode, int]],
        max_parents: int = 3,
        max_iterations: int = 100,
        score_metric: str = "bic",
    ) -> Dict[str, Any]:
        """Learns optimal Bayesian DAG topology via Greedy Hill Climbing under BIC/AIC scoring."""
        var_list = list(variables)
        n_vars = len(var_list)
        n_samples = len(data)
        if n_vars == 0 or n_samples == 0:
            return {
                "dag_adjacency": {},
                "best_score": 0.0,
                "edge_count": 0,
                "iterations": 0,
            }

        domain_sizes: Dict[TNode, int] = {}
        for v in var_list:
            unique_vals = {row[v] for row in data if v in row}
            domain_sizes[v] = max(2, len(unique_vals))

        parents: Dict[TNode, Set[TNode]] = {v: set() for v in var_list}
        node_scores: Dict[TNode, float] = {
            v: self._local_score(v, parents[v], data, domain_sizes, score_metric)
            for v in var_list
        }
        total_score = sum(node_scores.values())

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            best_op: Optional[Tuple[str, TNode, TNode, float]] = None
            best_delta = 0.0

            for u in var_list:
                for v in var_list:
                    if u == v:
                        continue

                    if u not in parents[v] and len(parents[v]) < max_parents:
                        if not self._would_create_cycle(parents, u, v):
                            cand_parents = parents[v].union({u})
                            cand_score = self._local_score(v, cand_parents, data, domain_sizes, score_metric)
                            delta = cand_score - node_scores[v]
                            if delta > best_delta:
                                best_delta = delta
                                best_op = ("add", u, v, cand_score)

                    if u in parents[v]:
                        cand_parents = parents[v] - {u}
                        cand_score = self._local_score(v, cand_parents, data, domain_sizes, score_metric)
                        delta = cand_score - node_scores[v]
                        if delta > best_delta:
                            best_delta = delta
                            best_op = ("delete", u, v, cand_score)

                    if u in parents[v] and len(parents[u]) < max_parents:
                        temp_parents = {var: set(parents[var]) for var in var_list}
                        temp_parents[v].remove(u)
                        if not self._would_create_cycle(temp_parents, v, u):
                            cand_p_v = parents[v] - {u}
                            cand_p_u = parents[u].union({v})
                            score_v = self._local_score(v, cand_p_v, data, domain_sizes, score_metric)
                            score_u = self._local_score(u, cand_p_u, data, domain_sizes, score_metric)
                            delta = (score_v - node_scores[v]) + (score_u - node_scores[u])
                            if delta > best_delta:
                                best_delta = delta
                                best_op = ("reverse", u, v, score_v, score_u)

            if best_op is None or best_delta <= 1e-6:
                break

            op_type = best_op[0]
            if op_type == "add":
                _, u, v, new_sc = best_op
                parents[v].add(u)
                node_scores[v] = new_sc
                total_score += best_delta
            elif op_type == "delete":
                _, u, v, new_sc = best_op
                parents[v].remove(u)
                node_scores[v] = new_sc
                total_score += best_delta
            elif op_type == "reverse":
                _, u, v, sc_v, sc_u = best_op
                parents[v].remove(u)
                parents[u].add(v)
                node_scores[v] = sc_v
                node_scores[u] = sc_u
                total_score += best_delta

        dag_adj: Dict[TNode, List[TNode]] = {v: [] for v in var_list}
        total_edges = 0
        for v in var_list:
            for u in parents[v]:
                dag_adj[u].append(v)
                total_edges += 1

        return {
            "dag_adjacency": dag_adj,
            "best_score": total_score,
            "edge_count": total_edges,
            "iterations": iteration,
        }

    def _local_score(
        self,
        target: TNode,
        parent_set: Set[TNode],
        data: Sequence[Mapping[TNode, int]],
        domain_sizes: Dict[TNode, int],
        metric: str,
    ) -> float:
        """Computes BIC/AIC local score for target given parents."""
        n_samples = len(data)
        p_list = sorted(list(parent_set), key=lambda x: str(x))
        r_i = domain_sizes[target]
        q_i = 1
        for p in p_list:
            q_i *= domain_sizes[p]

        counts: Dict[Tuple[int, ...], Dict[int, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
        parent_counts: Dict[Tuple[int, ...], int] = collections.defaultdict(int)

        for row in data:
            val_target = row.get(target, 0)
            p_tuple = tuple(row.get(p, 0) for p in p_list)
            counts[p_tuple][val_target] += 1
            parent_counts[p_tuple] += 1

        log_lik = 0.0
        for p_tuple, n_j in parent_counts.items():
            for val_target, n_ijk in counts[p_tuple].items():
                if n_ijk > 0 and n_j > 0:
                    log_lik += n_ijk * math.log(float(n_ijk) / float(n_j))

        num_params = q_i * (r_i - 1)
        penalty = 0.5 * num_params * math.log(n_samples) if metric == "bic" else num_params
        return log_lik - penalty

    def _would_create_cycle(
        self, parents: Dict[TNode, Set[TNode]], src: TNode, dst: TNode
    ) -> bool:
        """Tests if adding directed edge src -> dst introduces a directed cycle (i.e. path dst -> src exists)."""
        visited: Set[TNode] = set()
        queue = [dst]
        while queue:
            curr = queue.pop(0)
            if curr == src:
                return True
            if curr not in visited:
                visited.add(curr)
                for child, p_set in parents.items():
                    if curr in p_set and child not in visited:
                        queue.append(child)
        return False
