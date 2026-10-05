"""
================================================================================
ALGORITHM BLUEPRINT: QUERY ROUTING (ALGO-VEC-SRCH-98)
================================================================================

Query routing analyzes incoming user queries to determine the optimal retrieval
pipeline: keyword search (exact codes, IDs, symbols), dense vector search (conceptual,
natural language), hybrid sparse-dense, or multi-vector late interaction. It prevents
over-spending latency on simple exact lookups while steering complex semantic prompts
to high-capacity embedding indexes.
"""

from typing import Any, Dict, List, Optional
import re


class VectorSearchAlgoQueryRouting:
    """
    --- contract:
      id: ALGO-VEC-SRCH-98
      name: VectorSearchAlgoQueryRouting
      category: vector
      complexity: O(|Q|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query: str
        available_routes: list[str]
      output_schema:
        query: str
        selected_route: str
        confidence: float
        features_detected: dict[str, any]
        reasoning: str
    ---
    """

    @staticmethod
    def route_query(
        query: str,
        available_routes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not available_routes:
            available_routes = ["lexical_bm25", "dense_vector", "hybrid_sparse_dense", "direct_id_lookup"]

        tokens = re.findall(r"\w+", query)
        token_count = len(tokens)

        is_uuid = bool(re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}", query.lower()))
        has_error_code = bool(re.search(r"\b(ALGO|ERR|HTTP|STATUS)-\w+", query))
        has_quotes = '"' in query or "'" in query
        is_short = token_count <= 2

        features = {
            "token_count": token_count,
            "is_uuid": is_uuid,
            "has_error_code": has_error_code,
            "has_exact_quotes": has_quotes,
            "is_short": is_short,
        }

        if is_uuid or has_error_code:
            route = "direct_id_lookup" if "direct_id_lookup" in available_routes else available_routes[0]
            conf = 0.98
            reason = "Query contains explicit identifier or system error code"
        elif has_quotes or (is_short and not query.lower().startswith("what")):
            route = "lexical_bm25" if "lexical_bm25" in available_routes else available_routes[0]
            conf = 0.85
            reason = "Short keyword prompt or exact quoted string detected"
        elif token_count > 10:
            route = "dense_vector" if "dense_vector" in available_routes else available_routes[0]
            conf = 0.90
            reason = "Long natural language descriptive prompt optimal for embedding search"
        else:
            route = "hybrid_sparse_dense" if "hybrid_sparse_dense" in available_routes else available_routes[0]
            conf = 0.88
            reason = "General query benefiting from combined lexical and semantic scoring"

        return {
            "query": query,
            "selected_route": route,
            "confidence": conf,
            "features_detected": features,
            "reasoning": reason,
        }
