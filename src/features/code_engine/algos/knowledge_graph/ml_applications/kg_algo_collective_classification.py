r"""
================================================================================
ALGORITHM BLUEPRINT: ITERATIVE RELATIONAL CLASSIFIER & RELAXATION LABELING
================================================================================

1. OVERVIEW & OBJECTIVE:
   Collective classification engine implementing Iterative Classification (ICA),
   Weighted-Vote Relational Neighbor (wvRN), and probabilistic Relaxation Labeling
   for simultaneous entity node labeling in relational Knowledge Graphs. Fuses intrinsic
   node attribute priors with relational neighbor label distributions across iterations.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Ground Truth Anchoring: Known seed labels remain fixed (or clamped with confidence 1.0).
   - Convergence Guarantee: Tracks total label variance $\Delta P$ between consecutive rounds.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(T * (|V| * C + |E|)) where T is iterations and C is number of classes.
   - Space Complexity: O(|V| * C) for node posterior probability distribution tensors.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoCollectiveClassification:
    """
    --- contract:
      id: ALGO-KG-139
      name: KgAlgoCollectiveClassification
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Iter * (|V| * C + |E|))
        space: O(|V| * C)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - collective_classification
      - ica_algorithm
      - wvrn_relational
      - relaxation_labeling
      input_schema:
        nodes: array
        initial_labels: object
        edges: array
        iterations: integer
        relational_weight: number
      output_schema:
        algorithm: string
        final_labels: object
        class_probabilities: object
        iterations_run: integer
        converged: boolean
    ---
    """

    def iterative_classify(
        self,
        nodes: List[str],
        initial_labels: Dict[str, str],
        edges: List[Tuple[str, str]],
        iterations: int = 5,
        local_priors: Optional[Dict[str, Dict[str, float]]] = None,
        alpha_relational: float = 0.7,
        tolerance: float = 1e-4,
    ) -> Dict[str, Any]:
        all_classes: Set[str] = set(initial_labels.values())
        if local_priors:
            for p_dict in local_priors.values():
                all_classes.update(p_dict.keys())
        class_list = sorted(list(all_classes)) if all_classes else ["default"]

        adj: Dict[str, List[str]] = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        prob_dist: Dict[str, Dict[str, float]] = {}
        uniform_p = 1.0 / max(1, len(class_list))

        for n in nodes:
            if n in initial_labels:
                lbl = initial_labels[n]
                prob_dist[n] = {c: (1.0 if c == lbl else 0.0) for c in class_list}
            elif local_priors and n in local_priors:
                prob_dist[n] = dict(local_priors[n])
            else:
                prob_dist[n] = {c: uniform_p for c in class_list}

        converged = False
        actual_iters = 0

        for it in range(iterations):
            actual_iters += 1
            max_delta = 0.0
            next_probs: Dict[str, Dict[str, float]] = {}

            for n in nodes:
                if n in initial_labels:
                    next_probs[n] = dict(prob_dist[n])
                    continue

                neighbors = adj.get(n, [])
                nbr_dist: Dict[str, float] = {c: 0.0 for c in class_list}

                if neighbors:
                    for nbr in neighbors:
                        for c in class_list:
                            nbr_dist[c] += prob_dist.get(nbr, {}).get(c, uniform_p)
                    nbr_total = sum(nbr_dist.values()) or 1.0
                    for c in class_list:
                        nbr_dist[c] /= nbr_total
                else:
                    nbr_dist = {c: uniform_p for c in class_list}

                prior = local_priors.get(n, {c: uniform_p for c in class_list}) if local_priors else {c: uniform_p for c in class_list}
                prior_total = sum(prior.values()) or 1.0

                combined: Dict[str, float] = {}
                for c in class_list:
                    p_prior = prior.get(c, 0.0) / prior_total
                    p_rel = nbr_dist.get(c, 0.0)
                    combined[c] = ((1.0 - alpha_relational) * p_prior) + (alpha_relational * p_rel)

                comb_total = sum(combined.values()) or 1.0
                next_probs[n] = {c: combined[c] / comb_total for c in class_list}

                for c in class_list:
                    diff = abs(next_probs[n][c] - prob_dist[n][c])
                    if diff > max_delta:
                        max_delta = diff

            prob_dist = next_probs
            if max_delta < tolerance:
                converged = True
                break

        final_labels: Dict[str, str] = {}
        for n in nodes:
            best_c = max(prob_dist[n].items(), key=lambda x: x[1])[0]
            final_labels[n] = best_c

        return {
            "algorithm": "ALGO-KG-139",
            "final_labels": final_labels,
            "class_probabilities": {n: {c: round(p, 4) for c, p in probs.items()} for n, probs in prob_dist.items()},
            "iterations_run": actual_iters,
            "converged": converged,
        }
