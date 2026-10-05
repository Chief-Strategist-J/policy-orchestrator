"""
================================================================================
ALGORITHM BLUEPRINT: FRESH DISKANN IN-PLACE GRAPH UPDATE (ALGO-VEC-UPD-118)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements FreshDiskANN dual-index architecture: coordinates live writes to
   Mem-Vamana and periodically merges into immutable disk graph partitions.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoFreshDiskannUpdate:
    """
    --- contract:
      id: ALGO-VEC-UPD-118
      name: VectorUpdateAlgoFreshDiskannUpdate
      category: update
      complexity: O(|Mem| * log |Disk|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        disk_graph_nodes: list[str]
        mem_graph_nodes: list[str]
        deleted_nodes: list[str]
        new_records: list[str]
        mem_threshold: int
      output_schema:
        updated_mem_graph: list[str]
        updated_disk_graph: list[str]
        active_tombstones: list[str]
        merge_triggered: bool
    ---
    """

    @classmethod
    def execute(
        cls,
        disk_graph_nodes: List[str],
        mem_graph_nodes: List[str],
        deleted_nodes: List[str],
        new_records: List[str],
        mem_threshold: int = 500,
    ) -> Dict[str, Any]:
        mem = set(mem_graph_nodes)
        disk = set(disk_graph_nodes)
        tombs = set(deleted_nodes)

        for rec in new_records:
            mem.add(rec)
            tombs.discard(rec)

        merge_triggered = len(mem) >= mem_threshold
        if merge_triggered:
            disk.update(mem)
            disk.difference_update(tombs)
            mem.clear()
            tombs.clear()

        return {
            "updated_mem_graph": sorted(list(mem)),
            "updated_disk_graph": sorted(list(disk)),
            "active_tombstones": sorted(list(tombs)),
            "merge_triggered": merge_triggered,
            "mem_size": len(mem),
            "disk_size": len(disk),
        }
