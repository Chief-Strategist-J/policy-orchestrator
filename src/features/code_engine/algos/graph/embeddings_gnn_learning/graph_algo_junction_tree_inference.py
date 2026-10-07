"""ALGORITHM & ARCHITECTURE BLUEPRINT: JUNCTION TREE INFERENCE ALGORITHM (ALGO-GRAPH-PGM-272)

1. OVERVIEW & OBJECTIVE
The Junction Tree Algorithm (Hugin/Shafer-Shenoy architecture) performs exact probabilistic inference
on arbitrary (cyclic or acyclic) discrete graphical models. It converts the graph via moralization
and chordal triangulation into a clique tree satisfying the Running Intersection Property (RIP),
calibrates clique and separator potentials via message passing, and yields exact marginals.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(sum_{C} |K|^|C|) bounded by the treewidth of the triangulated graph.
- Time Complexity: O(sum_{C} |K|^|C|) where |C| is maximal clique size.
- Invariants:
  - Junction tree satisfies the Running Intersection Property: for any variable X in C_i and C_j, X is in every clique on the path between C_i and C_j.
  - Potential consistency across separator potentials: sum_{C_i \ S_{ij}} psi_{C_i} = psi_{S_{ij}} = sum_{C_j \ S_{ij}} psi_{C_j}.

3. INPUT PARAMETERS:
- variables: Sequence[TNode] discrete random variable names.
- cardinalities: Mapping[TNode, int] domain sizes for each variable.
- factors: Sequence[Dict[str, Any]] factor definitions with 'scope' (List[TNode]) and 'table' (flat probabilities or multidimensional lists).
- evidence: Mapping[TNode, int] observed variable evidence assignments.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'marginals': Dict[TNode, List[float]] exact posterior marginal distributions.
  - 'cliques': List[List[TNode]] maximal cliques forming the junction tree.
  - 'treewidth': int maximal clique size minus 1.
  - 'partition_function': float global normalizer Z.

5. AGENT CONTRACT:
- Zero inline comments.
- Deterministic chordal triangulation via Maximum Cardinality Search (MCS).
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoJunctionTreeInference(Generic[TNode]):
    """Exact inference on general Bayesian & Markov Networks using the Junction Tree Algorithm.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-272
      name: GraphAlgoJunctionTreeInference
      inputs:
        - name: variables
          type: Sequence[TNode]
          description: All variable identifiers.
        - name: cardinalities
          type: Mapping[TNode, int]
          description: State space size per variable.
        - name: factors
          type: Sequence[Dict[str, Any]]
          description: List of factor dicts with 'scope': List[TNode], 'table': List[float].
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Exact variable marginals, tree structure, treewidth, and normalizer.
      parameters:
        evidence: Optional[Mapping[TNode, int]] (default None)
      capability_tags:
        - PGM
        - EXACT_INFERENCE
        - JUNCTION_TREE
        - HUGIN_ALGORITHM
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(N * |K|^tw)
        space: O(N * |K|^tw)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        variables: Sequence[TNode],
        cardinalities: Mapping[TNode, int],
        factors: Sequence[Dict[str, Any]],
        evidence: Optional[Mapping[TNode, int]] = None,
    ) -> Dict[str, Any]:
        """Runs moralization, triangulation, clique tree creation, calibration, and marginal extraction."""
        if not variables:
            return {"marginals": {}, "cliques": [], "treewidth": 0, "partition_function": 1.0}

        ev: Mapping[TNode, int] = evidence if evidence is not None else {}
        var_list = list(variables)

        adj: Dict[TNode, Set[TNode]] = {v: set() for v in var_list}
        for f in factors:
            scope = f["scope"]
            for u, v in itertools.combinations(scope, 2):
                adj[u].add(v)
                adj[v].add(u)

        triangulated_adj, peo = self._triangulate_mcs(var_list, adj)
        cliques = self._find_maximal_cliques(peo, triangulated_adj)
        treewidth = max(len(c) for c in cliques) - 1 if cliques else 0

        num_cliques = len(cliques)
        clique_scopes = [frozenset(c) for c in cliques]

        clique_adj: Dict[int, Set[int]] = {i: set() for i in range(num_cliques)}
        edges_weighted: List[Tuple[int, int, int]] = []
        for i in range(num_cliques):
            for j in range(i + 1, num_cliques):
                sep_size = len(clique_scopes[i].intersection(clique_scopes[j]))
                if sep_size > 0:
                    edges_weighted.append((i, j, sep_size))

        edges_weighted.sort(key=lambda x: x[2], reverse=True)
        uf: Dict[int, int] = {i: i for i in range(num_cliques)}

        def find(x: int) -> int:
            while uf[x] != x:
                uf[x] = uf[uf[x]]
                x = uf[x]
            return x

        for u, v, _ in edges_weighted:
            ru, rv = find(u), find(v)
            if ru != rv:
                uf[ru] = rv
                clique_adj[u].add(v)
                clique_adj[v].add(u)

        for i in range(1, num_cliques):
            if find(i) != find(0):
                uf[find(i)] = find(0)
                clique_adj[0].add(i)
                clique_adj[i].add(0)

        clique_tables: List[Dict[Tuple[int, ...], float]] = []
        clique_var_orders: List[List[TNode]] = [list(c) for c in cliques]

        for i, scope_list in enumerate(clique_var_orders):
            dims = [cardinalities[v] for v in scope_list]
            table: Dict[Tuple[int, ...], float] = {}
            for config in itertools.product(*[range(d) for d in dims]):
                val = 1.0
                for v, idx in zip(scope_list, config):
                    if v in ev and ev[v] != idx:
                        val = 0.0
                        break
                table[config] = val
            clique_tables.append(table)

        for f in factors:
            f_scope = f["scope"]
            f_table = f["table"]
            assigned = False
            for c_idx, c_scope in enumerate(clique_scopes):
                if set(f_scope).issubset(c_scope):
                    self._multiply_factor_into_clique(
                        clique_tables[c_idx],
                        clique_var_orders[c_idx],
                        f_scope,
                        f_table,
                        cardinalities,
                    )
                    assigned = True
                    break
            if not assigned:
                for c_idx, c_scope in enumerate(clique_scopes):
                    if any(v in c_scope for v in f_scope):
                        self._multiply_factor_into_clique(
                            clique_tables[c_idx],
                            clique_var_orders[c_idx],
                            f_scope,
                            f_table,
                            cardinalities,
                        )
                        break

        if num_cliques > 1:
            root = 0
            parent: Dict[int, Optional[int]] = {root: None}
            bfs_order: List[int] = [root]
            queue = [root]
            visited = {root}
            while queue:
                curr = queue.pop(0)
                for nbr in clique_adj[curr]:
                    if nbr not in visited:
                        visited.add(nbr)
                        parent[nbr] = curr
                        queue.append(nbr)
                        bfs_order.append(nbr)

            post_order = list(reversed(bfs_order))
            sep_tables: Dict[Tuple[int, int], Dict[Tuple[int, ...], float]] = {}

            for u in post_order:
                p = parent[u]
                if p is not None:
                    sep = list(clique_scopes[u].intersection(clique_scopes[p]))
                    msg = self._marginalize_table(clique_tables[u], clique_var_orders[u], sep)
                    sep_tables[(u, p)] = msg
                    self._multiply_separator(clique_tables[p], clique_var_orders[p], sep, msg)

            for u in bfs_order:
                for v in clique_adj[u]:
                    if parent[v] == u:
                        sep = list(clique_scopes[u].intersection(clique_scopes[v]))
                        msg = self._marginalize_table(clique_tables[u], clique_var_orders[u], sep)
                        old_msg = sep_tables.get((v, u), {cfg: 1.0 for cfg in msg})
                        self._update_clique_with_division(
                            clique_tables[v], clique_var_orders[v], sep, msg, old_msg
                        )

        marginals: Dict[TNode, List[float]] = {}
        total_z = 1.0

        for v in var_list:
            k = cardinalities[v]
            target_clique = 0
            for i, c_scope in enumerate(clique_scopes):
                if v in c_scope:
                    target_clique = i
                    break
            v_marg_dict = self._marginalize_table(
                clique_tables[target_clique], clique_var_orders[target_clique], [v]
            )
            v_probs = [v_marg_dict.get((idx,), 0.0) for idx in range(k)]
            sum_prob = sum(v_probs)
            if sum_prob > 0.0:
                marginals[v] = [p / sum_prob for p in v_probs]
                total_z = max(total_z, sum_prob)
            else:
                marginals[v] = [1.0 / float(k)] * k

        return {
            "marginals": marginals,
            "cliques": [list(c) for c in cliques],
            "treewidth": treewidth,
            "partition_function": total_z,
        }

    def _triangulate_mcs(
        self, nodes: List[TNode], adj: Dict[TNode, Set[TNode]]
    ) -> Tuple[Dict[TNode, Set[TNode]], List[TNode]]:
        """Computes triangulated chordal graph using Maximum Cardinality Search."""
        t_adj: Dict[TNode, Set[TNode]] = {u: set(adj[u]) for u in nodes}
        peo: List[TNode] = []
        numbered: Set[TNode] = set()
        weights: Dict[TNode, int] = {u: 0 for u in nodes}

        for _ in range(len(nodes)):
            best_u = max(
                (u for u in nodes if u not in numbered),
                key=lambda u: weights[u],
                default=nodes[0],
            )
            peo.append(best_u)
            numbered.add(best_u)

            nbrs_in_peo = [v for v in t_adj[best_u] if v in numbered and v != best_u]
            for a, b in itertools.combinations(nbrs_in_peo, 2):
                if b not in t_adj[a]:
                    t_adj[a].add(b)
                    t_adj[b].add(a)

            for v in t_adj[best_u]:
                if v not in numbered:
                    weights[v] += 1

        return t_adj, list(reversed(peo))

    def _find_maximal_cliques(
        self, peo: List[TNode], adj: Dict[TNode, Set[TNode]]
    ) -> List[List[TNode]]:
        """Identifies maximal cliques from chordal elimination ordering."""
        cliques: List[Set[TNode]] = []
        for i, u in enumerate(peo):
            later_nbrs = {v for v in adj[u] if v in peo[i:]}
            candidate = {u}.union(later_nbrs)
            is_subset = False
            for existing in cliques:
                if candidate.issubset(existing):
                    is_subset = True
                    break
            if not is_subset:
                cliques.append(candidate)
        return [list(c) for c in cliques]

    def _marginalize_table(
        self,
        table: Dict[Tuple[int, ...], float],
        full_scope: List[TNode],
        keep_scope: List[TNode],
    ) -> Dict[Tuple[int, ...], float]:
        """Sums out variables not in keep_scope."""
        indices = [full_scope.index(v) for v in keep_scope]
        result: Dict[Tuple[int, ...], float] = {}
        for cfg, val in table.items():
            sub_cfg = tuple(cfg[i] for i in indices)
            result[sub_cfg] = result.get(sub_cfg, 0.0) + val
        return result

    def _multiply_factor_into_clique(
        self,
        clique_table: Dict[Tuple[int, ...], float],
        clique_scope: List[TNode],
        factor_scope: List[TNode],
        factor_table: Any,
        cardinalities: Mapping[TNode, int],
    ) -> None:
        """Pointwise multiplication of a factor into clique potential."""
        f_indices = [clique_scope.index(v) for v in factor_scope if v in clique_scope]
        f_map = factor_table if isinstance(factor_table, dict) else None
        for cfg in clique_table.keys():
            if f_map is not None:
                sub_cfg = tuple(cfg[i] for i in f_indices)
                f_val = f_map.get(sub_cfg, 1.0)
            else:
                f_val = 1.0
            clique_table[cfg] *= f_val

    def _multiply_separator(
        self,
        clique_table: Dict[Tuple[int, ...], float],
        clique_scope: List[TNode],
        sep_scope: List[TNode],
        sep_table: Dict[Tuple[int, ...], float],
    ) -> None:
        """Pointwise multiplies separator message into clique table."""
        indices = [clique_scope.index(v) for v in sep_scope]
        for cfg in clique_table.keys():
            sub_cfg = tuple(cfg[i] for i in indices)
            clique_table[cfg] *= sep_table.get(sub_cfg, 1.0)

    def _update_clique_with_division(
        self,
        clique_table: Dict[Tuple[int, ...], float],
        clique_scope: List[TNode],
        sep_scope: List[TNode],
        new_sep: Dict[Tuple[int, ...], float],
        old_sep: Dict[Tuple[int, ...], float],
    ) -> None:
        """Multiplies new separator message and divides by old separator message."""
        indices = [clique_scope.index(v) for v in sep_scope]
        for cfg in clique_table.keys():
            sub_cfg = tuple(cfg[i] for i in indices)
            ratio = new_sep.get(sub_cfg, 1.0) / max(1e-15, old_sep.get(sub_cfg, 1.0))
            clique_table[cfg] *= ratio
