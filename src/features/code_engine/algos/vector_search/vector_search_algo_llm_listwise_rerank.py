"""
================================================================================
ALGORITHM BLUEPRINT: LLM LISTWISE RERANKING (ALGO-VEC-SRCH-96)
================================================================================

LLM listwise reranking prompts an LLM with the query and the complete candidate list
simultaneously, asking it to output an ordered permutation list (e.g. [3] > [1] > [4]).
This models complex cross-document interactions and mutual information, avoiding
pairwise score variance and enabling global relevance judgments.
"""

from typing import Any, Dict, List, Optional
import re


class VectorSearchAlgoLLMListwiseRerank:
    """
    --- contract:
      id: ALGO-VEC-SRCH-96
      name: VectorSearchAlgoLLMListwiseRerank
      category: vector
      complexity: O(L_prompt + |candidates|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query: str
        candidates: list[dict[str, any]]
        simulated_llm_response: str
        top_k: int
      output_schema:
        query: str
        candidate_count: int
        generated_prompt: str
        parsed_order: list[int]
        reranked_results: list[dict[str, any]]
    ---
    """

    @staticmethod
    def build_prompt(query: str, candidates: List[Dict[str, Any]]) -> str:
        prompt_lines = [
            f"Query: {query}",
            "Below is a list of candidate passages. Rank them from most relevant to least relevant.",
            "Format your answer as a list of IDs in descending relevance order, e.g. [1] > [2] > [3].",
            "",
        ]
        for idx, cand in enumerate(candidates):
            text = cand.get("text", "")
            prompt_lines.append(f"[{idx}] {text}")

        prompt_lines.append("")
        prompt_lines.append("Ranking:")
        return "\n".join(prompt_lines)

    @staticmethod
    def parse_ranking(ranking_str: str, candidate_count: int) -> List[int]:
        found_ids = [int(m) for m in re.findall(r"\[?(\d+)\]?", ranking_str)]
        seen = set()
        clean_order = []
        for fid in found_ids:
            if 0 <= fid < candidate_count and fid not in seen:
                clean_order.append(fid)
                seen.add(fid)

        for i in range(candidate_count):
            if i not in seen:
                clean_order.append(i)

        return clean_order

    @staticmethod
    def rerank(
        query: str,
        candidates: List[Dict[str, Any]],
        simulated_llm_response: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        prompt = VectorSearchAlgoLLMListwiseRerank.build_prompt(query, candidates)

        if not simulated_llm_response:
            simulated_llm_response = " > ".join(f"[{i}]" for i in range(len(candidates)))

        order = VectorSearchAlgoLLMListwiseRerank.parse_ranking(
            simulated_llm_response, len(candidates)
        )

        ranked: List[Dict[str, Any]] = []
        for rank_pos, idx in enumerate(order):
            cand = candidates[idx]
            ranked.append({
                "id": cand.get("id"),
                "original_index": idx,
                "rank": rank_pos + 1,
                "text": cand.get("text", "")[:80],
                "metadata": cand.get("metadata", {}),
            })

        return {
            "query": query,
            "candidate_count": len(candidates),
            "generated_prompt": prompt,
            "parsed_order": order,
            "reranked_results": ranked[:top_k],
        }
