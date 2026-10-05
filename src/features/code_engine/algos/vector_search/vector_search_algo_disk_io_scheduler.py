"""
================================================================================
ALGORITHM BLUEPRINT: DISK I/O SCHEDULER (ALGO-VEC-SRCH-108)
================================================================================

Disk I/O scheduling optimizes SSD access during disk-based graph and partition
traversal (DiskANN, SPANN). Vector data and graph adjacency are packed into aligned
4 KB page sectors. At each beam search hop, requests for multiple candidate node
sectors are batched into a single asynchronous multi-read queue (io_uring), eliminating
single-read serial latency.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoDiskIOScheduler:
    """
    --- contract:
      id: ALGO-VEC-SRCH-108
      name: VectorSearchAlgoDiskIOScheduler
      category: vector
      complexity: O(|node_ids|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        requested_node_ids: list[int]
        bytes_per_node: int
        cached_nodes: list[int]
        page_size_bytes: int
      output_schema:
        total_requested: int
        cache_hits: int
        disk_reads_required: int
        io_batches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def schedule_reads(
        requested_node_ids: List[int],
        bytes_per_node: int = 512,
        cached_nodes: Optional[List[int]] = None,
        page_size_bytes: int = 4096,
        max_batch_size: int = 8,
    ) -> Dict[str, Any]:
        if not requested_node_ids:
            return {
                "total_requested": 0,
                "cache_hits": 0,
                "disk_reads_required": 0,
                "io_batches": [],
            }

        cache_set = set(cached_nodes) if cached_nodes else set()
        to_read = []
        cache_hits = 0

        for nid in requested_node_ids:
            if nid in cache_set:
                cache_hits += 1
            else:
                to_read.append(nid)

        batches: List[Dict[str, Any]] = []
        nodes_per_page = max(1, page_size_bytes // max(1, bytes_per_node))

        current_batch_pages = set()
        current_batch_nodes = []

        for nid in to_read:
            page_id = nid // nodes_per_page
            current_batch_pages.add(page_id)
            current_batch_nodes.append(nid)

            if len(current_batch_nodes) >= max_batch_size:
                batches.append({
                    "batch_id": len(batches),
                    "node_count": len(current_batch_nodes),
                    "distinct_pages": len(current_batch_pages),
                    "node_ids": current_batch_nodes,
                })
                current_batch_pages = set()
                current_batch_nodes = []

        if current_batch_nodes:
            batches.append({
                "batch_id": len(batches),
                "node_count": len(current_batch_nodes),
                "distinct_pages": len(current_batch_pages),
                "node_ids": current_batch_nodes,
            })

        return {
            "total_requested": len(requested_node_ids),
            "cache_hits": cache_hits,
            "disk_reads_required": len(to_read),
            "io_batches": batches,
        }
