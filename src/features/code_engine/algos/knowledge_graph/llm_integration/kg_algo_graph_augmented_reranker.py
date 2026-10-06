"""
GRAPH CONNECTIVITY AWARE PASSAGE RERANKER
Implementation Module for KgAlgoGraphAugmentedReranker (ALGO-KG-184).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoGraphAugmentedReranker:
    """
    --- contract:
      id: ALGO-KG-184
      name: KgAlgoGraphAugmentedReranker
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Passages * KG_Lookups)
        space: O(Passages)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graph_reranker
      - topological_boost
      - retrieval_refinement
      input_schema:
        passages: array
        query_entities: array
        kg_adj: object
      output_schema:
        algorithm: string
        ranked_passages: array
    ---
    """
    def rerank(self, passages: List[Dict[str, Any]], query_entities: List[str], kg_adj: Dict[str, List[str]], graph_weight: float = 0.3) -> Dict[str, Any]:
        query_set = set(query_entities)
        reranked: List[Dict[str, Any]] = []
        for p in passages:
            base_score = p.get("score", 0.5)
            p_entities = p.get("entities", [])
            overlap = len(set(p_entities) & query_set)
            connected = 0
            for pe in p_entities:
                for qe in query_entities:
                    if pe in kg_adj.get(qe, []):
                        connected += 1
            graph_score = min(1.0, (overlap * 0.5) + (connected * 0.25))
            final_score = ((1.0 - graph_weight) * base_score) + (graph_weight * graph_score)
            item = dict(p)
            item["final_score"] = round(final_score, 4)
            reranked.append(item)
        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return {
            "algorithm": "ALGO-KG-184",
            "ranked_passages": reranked,
        }
