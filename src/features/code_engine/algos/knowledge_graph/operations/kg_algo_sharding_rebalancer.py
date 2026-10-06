"""
GRAPH SHARD REBALANCING AND LOAD EQUALIZER
Implementation Module for KgAlgoShardingRebalancer (ALGO-KG-170).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoShardingRebalancer:
    """
    --- contract:
      id: ALGO-KG-170
      name: KgAlgoShardingRebalancer
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Shards * Elements)
        space: O(Shards)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - shard_rebalancer
      - load_equalization
      - migration_planner
      input_schema:
        shard_allocations: object
      output_schema:
        algorithm: string
        migration_plan: array
    ---
    """
    def compute_migrations(self, shards: Dict[str, List[str]]) -> Dict[str, Any]:
        total_items = sum(len(v) for v in shards.values())
        num_shards = max(1, len(shards))
        target_per_shard = total_items // num_shards
        overloaded = [(k, len(v) - target_per_shard) for k, v in shards.items() if len(v) > target_per_shard]
        underloaded = [(k, target_per_shard - len(v)) for k, v in shards.items() if len(v) < target_per_shard]
        migrations: List[Dict[str, Any]] = []
        for src_k, surplus in overloaded:
            for tgt_k, deficit in underloaded:
                if surplus <= 0:
                    break
                move_count = min(surplus, deficit)
                if move_count > 0:
                    migrations.append({"from_shard": src_k, "to_shard": tgt_k, "count": move_count})
                    surplus -= move_count
        return {
            "algorithm": "ALGO-KG-170",
            "migration_plan": migrations,
            "total_migrations": len(migrations),
        }
