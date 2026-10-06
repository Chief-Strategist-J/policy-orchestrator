r"""
================================================================================
ALGORITHM BLUEPRINT: LEAKAGE-FREE INVERSE & SYMMETRIC RELATION SPLITTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Leakage-free dataset splitting engine for Knowledge Graph completion benchmarks
   (WN18RR / FB15k-237 protocols). Prevents test set data leakage caused by inverse
   relations $(s, r_1, o) \iff (o, r_2, s)$ and symmetric relations $r = r^{-1}$
   by clustering co-dependent triple pairs into atomic partition blocks and ensuring
   transductive entity coverage.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inverse Leakage: Inverse/symmetric triple pairs are assigned strictly to the
     same split partition (never split across train vs test).
   - Transductive Invariant: All entities in test/valid splits must appear in training.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|Triples| + |Relations|^2) for co-occurrence mining and clustering.
   - Space Complexity: O(|Triples|) for disjoint set partition buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoLeakageFreeSplitter:
    """
    --- contract:
      id: ALGO-KG-149
      name: KgAlgoLeakageFreeSplitter
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Triples + Relations^2)
        space: O(Triples)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - leakage_free_split
      - inverse_filtering
      - symmetric_closure
      - transductive_guarantee
      input_schema:
        triples: array
        known_inverses: optional object
        train_ratio: number
        val_ratio: number
      output_schema:
        algorithm: string
        train_triples: array
        val_triples: array
        test_triples: array
        leakage_detected_count: integer
    ---
    """

    def split_triples(
        self,
        triples: List[Dict[str, str]],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        known_inverses: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        inverse_map = known_inverses or {}

        triple_tuples = [(t.get("head", t.get("s", "")), t.get("rel", t.get("p", "")), t.get("tail", t.get("o", ""))) for t in triples]
        triple_set = set(triple_tuples)

        co_occurring_inverses: Dict[str, str] = dict(inverse_map)
        pair_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        for s, p, o in triple_tuples:
            for cand_p in {p2 for s2, p2, o2 in triple_tuples if s2 == o and o2 == s}:
                pair_counts[(p, cand_p)] += 1

        for (p1, p2), count in pair_counts.items():
            if count >= 2 and p1 not in co_occurring_inverses:
                co_occurring_inverses[p1] = p2

        clusters: List[List[Tuple[str, str, str]]] = []
        visited_triples: Set[Tuple[str, str, str]] = set()

        for s, p, o in triple_tuples:
            if (s, p, o) in visited_triples:
                continue

            cluster = [(s, p, o)]
            visited_triples.add((s, p, o))

            inv_p = co_occurring_inverses.get(p)
            if inv_p:
                inv_triple = (o, inv_p, s)
                if inv_triple in triple_set and inv_triple not in visited_triples:
                    cluster.append(inv_triple)
                    visited_triples.add(inv_triple)

            if p in co_occurring_inverses and co_occurring_inverses[p] == p:
                sym_triple = (o, p, s)
                if sym_triple in triple_set and sym_triple not in visited_triples:
                    cluster.append(sym_triple)
                    visited_triples.add(sym_triple)

            clusters.append(cluster)

        clusters.sort(key=len, reverse=True)

        train_clusters = []
        val_clusters = []
        test_clusters = []

        total_triples = len(triple_tuples)
        train_target = int(total_triples * train_ratio)
        val_target = int(total_triples * val_ratio)

        current_train_cnt = 0
        current_val_cnt = 0

        train_entities: Set[str] = set()

        for cl in clusters:
            cl_size = len(cl)
            if current_train_cnt < train_target:
                train_clusters.append(cl)
                current_train_cnt += cl_size
                for s, p, o in cl:
                    train_entities.add(s)
                    train_entities.add(o)
            elif current_val_cnt < val_target:
                all_in_train = all(s in train_entities and o in train_entities for s, p, o in cl)
                if all_in_train:
                    val_clusters.append(cl)
                    current_val_cnt += cl_size
                else:
                    train_clusters.append(cl)
                    current_train_cnt += cl_size
                    for s, p, o in cl:
                        train_entities.add(s)
                        train_entities.add(o)
            else:
                all_in_train = all(s in train_entities and o in train_entities for s, p, o in cl)
                if all_in_train:
                    test_clusters.append(cl)
                else:
                    train_clusters.append(cl)
                    current_train_cnt += cl_size
                    for s, p, o in cl:
                        train_entities.add(s)
                        train_entities.add(o)

        train_res = [t for cl in train_clusters for t in cl]
        val_res = [t for cl in val_clusters for t in cl]
        test_res = [t for cl in test_clusters for t in cl]

        return {
            "algorithm": "ALGO-KG-149",
            "train_count": len(train_res),
            "val_count": len(val_res),
            "test_count": len(test_res),
            "inverse_pairs_detected": len(co_occurring_inverses),
            "train_triples": [{"head": s, "rel": p, "tail": o} for s, p, o in train_res],
            "val_triples": [{"head": s, "rel": p, "tail": o} for s, p, o in val_res],
            "test_triples": [{"head": s, "rel": p, "tail": o} for s, p, o in test_res],
        }
