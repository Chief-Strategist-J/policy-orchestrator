"""
================================================================================
ALGORITHM BLUEPRINT: RETRIEVAL & VECTOR STORAGE COST ACCOUNTING (ALGO-VEC-OBS-199)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Accounts for dollar economics of retrieval requests and storage footprint across
   embedding tokens, cross-encoder reranking, GPU compute, and memory RAM usage.

2. MATHEMATICAL FORMULATION:
   QueryCost = (tokens * price_embed) + (rerank_docs * price_rerank) + (gpu_ms * price_gpu)
   StorageCostMonthly = (num_vectors * bytes_per_vec / 1e9) * price_per_gb_month
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoCostAccounting:
    """
    --- contract:
      id: ALGO-VEC-OBS-199
      name: VectorObservabilityAlgoCostAccounting
      category: observability
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        queries_count: int
        total_tokens_embedded: int
        total_reranked_passages: int
        indexed_vector_count: int
        vector_dimension: int
        precision_bytes: int
        unit_prices: Optional[dict[str, float]]
      output_schema:
        embedding_compute_cost_usd: float
        reranking_cost_usd: float
        monthly_storage_cost_usd: float
        total_retrieval_cost_usd: float
        cost_per_1000_queries_usd: float
    ---
    """

    @classmethod
    def calculate_cost(
        cls,
        queries_count: int = 10000,
        total_tokens_embedded: int = 500000,
        total_reranked_passages: int = 50000,
        indexed_vector_count: int = 1000000,
        vector_dimension: int = 768,
        precision_bytes: int = 4,
        unit_prices: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        prices = unit_prices or {
            "price_per_1m_embed_tokens": 0.02,
            "price_per_1k_rerank_docs": 0.002,
            "price_per_gb_ram_monthly": 4.00,
        }

        embed_price = prices.get("price_per_1m_embed_tokens", 0.02)
        rerank_price = prices.get("price_per_1k_rerank_docs", 0.002)
        ram_price = prices.get("price_per_gb_ram_monthly", 4.00)

        embed_cost = (total_tokens_embedded / 1000000.0) * embed_price
        rerank_cost = (total_reranked_passages / 1000.0) * rerank_price

        raw_bytes = indexed_vector_count * vector_dimension * precision_bytes
        gb_used = raw_bytes / (1024.0 ** 3)
        storage_monthly_cost = gb_used * ram_price

        total_retrieval = embed_cost + rerank_cost
        cost_per_1k = (total_retrieval / float(queries_count) * 1000.0) if queries_count > 0 else 0.0

        return {
            "embedding_compute_cost_usd": round(embed_cost, 4),
            "reranking_cost_usd": round(rerank_cost, 4),
            "monthly_storage_cost_usd": round(storage_monthly_cost, 2),
            "total_retrieval_cost_usd": round(total_retrieval, 4),
            "cost_per_1000_queries_usd": round(cost_per_1k, 4),
        }
