"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: NPROBE MULTI-PROBE TUNER (ALGO-VEC-SRCH-63)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dynamically calibrates and tunes the `nprobe` parameter (#63) for IVF indexes.
   Empirically sweeps candidate nprobe values on sampled queries against brute-force
   ground truth (V5 rule), generating a Pareto frontier of Recall@k versus
   query latency/candidate evaluations. Selects the optimal parameter meeting a target recall SLO.

2. ALGORITHMIC MECHANICS:
   - Evaluates exact top-k for sampled queries via brute force (#51).
   - Iterates through candidate nprobe values in ascending order.
   - For each nprobe setting, records:
     - Intersection recall@k: |retrieved_k ∩ ground_truth_k| / k
     - Average candidate vectors probed per query
   - Identifies the minimum nprobe satisfying `target_recall`.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Ground Truth Parity: Compares exact set equality on IDs.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
import numpy as np
from src.features.code_engine.algos.vector_search.vector_search_algo_brute_force_gemm import VectorSearchAlgoBruteForceGemm
from src.features.code_engine.algos.vector_search.vector_search_algo_ivf import VectorSearchAlgoIvf


class VectorSearchAlgoNprobeTuner:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-63
      name: VectorSearchAlgoNprobeTuner
      version: 1.0.0
      category: vector
      capability_tags: [vector, nprobe, tuning, pareto_frontier, recall_optimization]
      inputs:
        type: object
        required: [database_vectors, sample_queries]
        properties:
          database_vectors:
            type: array
            items:
              type: array
              items: {type: number}
          sample_queries:
            type: array
            items:
              type: array
              items: {type: number}
          target_recall: {type: number, default: 0.9}
          k: {type: integer, default: 5}
          num_clusters: {type: integer, default: 8}
          nprobe_candidates:
            type: array
            items: {type: integer}
      outputs:
        type: object
        required: [recommended_nprobe, target_recall, achieved_recall, sweep_results]
        properties:
          recommended_nprobe: {type: integer}
          target_recall: {type: number}
          achieved_recall: {type: number}
          sweep_results:
            type: array
            items:
              type: object
              properties:
                nprobe: {type: integer}
                mean_recall: {type: number}
                avg_candidates: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N * C + len(queries) * (N + |sweep| * candidates))
        space: O(N * D)
      preconditions:
        - len(input.database_vectors) > 0
        - len(input.sample_queries) > 0
      postconditions:
        - output.recommended_nprobe >= 1
      compatible_adapters:
        - ADAPTER-TUNER-REPORT
    ---
    """

    @classmethod
    def tune_nprobe(
        cls,
        database_vectors: Union[List[List[float]], np.ndarray],
        sample_queries: Union[List[List[float]], np.ndarray],
        target_recall: float = 0.9,
        k: int = 5,
        num_clusters: int = 8,
        nprobe_candidates: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        X = np.asarray(database_vectors, dtype=np.float32)
        Q = np.asarray(sample_queries, dtype=np.float32)

        N, D = X.shape
        num_q = Q.shape[0]

        if nprobe_candidates is None:
            candidates = [1, 2, 4, 8]
        else:
            candidates = sorted(list(set(nprobe_candidates)))

        candidates = [p for p in candidates if 1 <= p <= num_clusters]
        if not candidates:
            candidates = [1]

        gt_search = VectorSearchAlgoBruteForceGemm.search(X, Q, k=k, metric="l2")
        gt_results = gt_search["results"]

        ground_truth_sets = [
            set(match["id"] for match in q_res["matches"])
            for q_res in gt_results
        ]

        sweep_results: List[Dict[str, Any]] = []
        recommended_nprobe = candidates[-1]
        best_achieved_recall = 0.0

        for probe_val in candidates:
            recalls: List[float] = []
            cand_counts: List[int] = []

            for q_idx in range(num_q):
                q = Q[q_idx]
                ivf_res = VectorSearchAlgoIvf.search(
                    X,
                    q,
                    k=k,
                    num_clusters=num_clusters,
                    nprobe=probe_val,
                )
                cand_counts.append(ivf_res["total_candidates"])
                retrieved_ids = set(match["id"] for match in ivf_res["matches"])
                gt_set = ground_truth_sets[q_idx]

                if gt_set:
                    recall_val = len(retrieved_ids.intersection(gt_set)) / len(gt_set)
                else:
                    recall_val = 1.0
                recalls.append(recall_val)

            mean_rec = float(np.mean(recalls)) if recalls else 0.0
            avg_cand = float(np.mean(cand_counts)) if cand_counts else 0.0

            sweep_results.append({
                "nprobe": probe_val,
                "mean_recall": mean_rec,
                "avg_candidates": avg_cand,
            })

            if mean_rec >= target_recall and recommended_nprobe == candidates[-1]:
                recommended_nprobe = probe_val
                best_achieved_recall = mean_rec

        if best_achieved_recall == 0.0 and sweep_results:
            best_entry = max(sweep_results, key=lambda x: x["mean_recall"])
            recommended_nprobe = best_entry["nprobe"]
            best_achieved_recall = best_entry["mean_recall"]

        return {
            "recommended_nprobe": recommended_nprobe,
            "target_recall": target_recall,
            "achieved_recall": best_achieved_recall,
            "num_clusters": num_clusters,
            "sample_queries_count": num_q,
            "sweep_results": sweep_results,
        }
