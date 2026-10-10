from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoReverseModeAutodiff:
    """
    ---
    contract:
      algo_id: ALGO-NN-23
      name: NnAlgoReverseModeAutodiff
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.autodiff
        - nn.reverse_mode
        - nn.computational_graph
        - nn.vjp
      inputs:
        type: object
        properties:
          nodes:
            type: array
            items:
              type: object
              properties:
                id:
                  type: integer
                op:
                  type: string
                  enum: [input, add, mul, relu, sin, exp, sum]
                parents:
                  type: array
                  items:
                    type: integer
                value:
                  type: number
            description: Ordered execution tape of DAG nodes in topological order.
          target_node_id:
            type: integer
            description: Node ID corresponding to the scalar loss output to differentiate from.
        required:
          - nodes
          - target_node_id
        additionalProperties: false
      outputs:
        type: object
        properties:
          node_values:
            type: array
            items:
              type: number
            description: Forward evaluated scalar values for all nodes in tape.
          adjoints:
            type: array
            items:
              type: number
            description: Reverse-mode accumulated adjoint gradients dL/dv_i for all nodes.
          tape_length:
            type: integer
            description: Total number of recorded computational graph operations.
        required:
          - node_values
          - adjoints
          - tape_length
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        nodes: Sequence[Dict[str, Any]],
        target_node_id: int,
    ) -> Dict[str, Any]:
        num_nodes = len(nodes)
        if num_nodes == 0:
            raise ValueError("Precondition failed: computational tape cannot be empty.")
        if not (0 <= target_node_id < num_nodes):
            raise ValueError(f"Precondition failed: target_node_id {target_node_id} out of bounds.")

        # Forward pass evaluation
        values: List[float] = [0.0] * num_nodes
        for i, node in enumerate(nodes):
            op = node.get("op", "input")
            parents = node.get("parents", [])

            if op == "input":
                values[i] = float(node.get("value", 0.0))
            elif op == "add":
                values[i] = values[parents[0]] + values[parents[1]]
            elif op == "mul":
                values[i] = values[parents[0]] * values[parents[1]]
            elif op == "relu":
                values[i] = max(0.0, values[parents[0]])
            elif op == "sin":
                values[i] = math.sin(values[parents[0]])
            elif op == "exp":
                values[i] = math.exp(values[parents[0]])
            elif op == "sum":
                values[i] = sum(values[p] for p in parents)
            else:
                raise ValueError(f"Precondition failed: unsupported op {op}")

        # Reverse pass adjoint accumulation
        adjoints: List[float] = [0.0] * num_nodes
        adjoints[target_node_id] = 1.0  # seed gradient dL/dL = 1

        for i in range(num_nodes - 1, -1, -1):
            adj = adjoints[i]
            if adj == 0.0:
                continue
            node = nodes[i]
            op = node.get("op", "input")
            parents = node.get("parents", [])

            if op == "add":
                adjoints[parents[0]] += adj
                adjoints[parents[1]] += adj
            elif op == "mul":
                p0, p1 = parents[0], parents[1]
                adjoints[p0] += adj * values[p1]
                adjoints[p1] += adj * values[p0]
            elif op == "relu":
                p0 = parents[0]
                grad_val = 1.0 if values[p0] > 0.0 else 0.0
                adjoints[p0] += adj * grad_val
            elif op == "sin":
                p0 = parents[0]
                adjoints[p0] += adj * math.cos(values[p0])
            elif op == "exp":
                p0 = parents[0]
                adjoints[p0] += adj * values[i]
            elif op == "sum":
                for p in parents:
                    adjoints[p] += adj

        return {
            "node_values": values,
            "adjoints": adjoints,
            "tape_length": num_nodes,
        }
