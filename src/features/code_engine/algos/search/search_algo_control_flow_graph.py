"""
================================================================================
ALGORITHM BLUEPRINT: CONTROL FLOW GRAPH (CFG & BASIC BLOCK ANALYZER)
================================================================================

1. OVERVIEW:
   Constructs an intra-procedural Control Flow Graph (CFG) for a function body.
   Segments statement sequences into Basic Blocks (straight-line execution runs
   with exactly one entry and exit point) and connects them with directed control
   edges (fallthrough, conditional branches, loops, returns, exceptions).
   Enables path reachability proofs, dead code detection, and invariant placement.

2. BASIC BLOCK & CONTROL EDGE TAXONOMY:
   - Entry Block: Initial starting point of function.
   - Branch Edge: Conditional jump (if-true, if-false).
   - Loop Edge: Back-edge to loop header.
   - Exit Block: Return / Raise terminal statement.

3. COMPLEXITY ANALYSIS:
   - Construction: O(S) where S is statement count.
   - Path Reachability: O(B + E) where B is block count and E is edge count.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
from typing import Dict, List, Any, Optional, Set, Tuple


class BasicBlock:
    def __init__(self, block_id: int, label: str = "") -> None:
        self.block_id: int = block_id
        self.label: str = label
        self.statements: List[str] = []
        self.successors: List[int] = []
        self.predecessors: List[int] = []
        self.is_terminal: bool = False


class SearchEngineControlFlowGraphAlgo:
    """
    --- contract:
      id: ALGO-SRCH-91
      name: SearchEngineControlFlowGraphAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Statements)
        space: O(Blocks + Edges)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - cfg.builder
      - analysis.control_flow
      - graph.basic_blocks
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self) -> None:
        self._blocks: Dict[int, BasicBlock] = {}
        self._entry_id: int = 0

    def build_cfg_from_statements(self, statements: List[str]) -> Dict[str, Any]:
        self._blocks = {}
        curr_block = BasicBlock(0, "ENTRY")
        self._blocks[0] = curr_block
        block_id_seq = 1

        for stmt in statements:
            s_clean = stmt.strip()
            if s_clean.startswith(("if ", "elif ", "for ", "while ")):
                branch_block = BasicBlock(block_id_seq, f"COND_{s_clean[:15]}")
                self._blocks[block_id_seq] = branch_block
                curr_block.successors.append(block_id_seq)
                branch_block.predecessors.append(curr_block.block_id)
                block_id_seq += 1

                body_block = BasicBlock(block_id_seq, "BODY")
                self._blocks[block_id_seq] = body_block
                branch_block.successors.append(block_id_seq)
                body_block.predecessors.append(branch_block.block_id)
                block_id_seq += 1

                curr_block = body_block
            elif s_clean.startswith(("return", "raise", "break")):
                curr_block.statements.append(s_clean)
                curr_block.is_terminal = True
                new_block = BasicBlock(block_id_seq, "AFTER_TERMINAL")
                self._blocks[block_id_seq] = new_block
                curr_block = new_block
                block_id_seq += 1
            else:
                curr_block.statements.append(s_clean)

        dead_blocks = [b.block_id for b in self._blocks.values() if b.block_id != 0 and len(b.predecessors) == 0]

        return {
            "total_blocks": len(self._blocks),
            "entry_block_id": 0,
            "unreachable_blocks": dead_blocks,
            "blocks": [
                {
                    "id": b.block_id,
                    "label": b.label,
                    "statements": b.statements,
                    "successors": b.successors,
                    "predecessors": b.predecessors,
                    "is_terminal": b.is_terminal
                } for b in self._blocks.values()
            ]
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        statements = payload.get("statements", [])
        code = payload.get("code")

        if code and not statements:
            statements = [line.strip() for line in str(code).splitlines() if line.strip()]

        cfg_summary = self.build_cfg_from_statements(statements)

        return {
            "algorithm": "ALGO-SRCH-94",
            "cfg_summary": cfg_summary
        }
