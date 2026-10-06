"""
================================================================================
ALGORITHM BLUEPRINT: MYERS O(ND) DIFFERENCE ALGORITHM (SHORTEST EDIT SCRIPT)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Eugene W. Myers' $O((N+M)D)$ greedy diff algorithm formulates sequence
   comparison as finding the shortest path through an edit graph from $(0,0)$
   to $(N, M)$. Progresses along diagonals $k = x - y$, taking snakes
   (diagonal matches) greedily for free. Finds the optimal Shortest Edit Script (SES)
   proportional to edit distance $D$ rather than $(N \times M)$.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Diagonal Invariant: Along diagonal $k$, $x - y = k$.
   - Greedy Snake Invariant: Whenever $A[x] == B[y]$, continue along the diagonal
     without incrementing edit cost $D$.
   - Minimum Edit Distance: Terminate immediately on the first $D$ that reaches $(N, M)$.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: $O((N + M) D)$ where $D$ is the size of the minimal edit script
   - Space Complexity: $O((N + M) D)$ for full path reconstruction
   - Best Case: $O(N)$ when sequences are nearly identical ($D \ll N$).

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class CodeEngineMyersDiffAlgo:
    """
    --- contract:
      id: ALGO-DIFF-146
      name: CodeEngineMyersDiffAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O((N + M) * D) where D is edit count
        space: O((N + M) * D)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.myers_ond
      - edit_graph.shortest_path
      - git_diff.line_comparison
      input_schema:
        source_lines: array
        target_lines: array
      output_schema:
        algorithm: string
        edit_distance: integer
        diff_hunks: array
        script: array
    ---
    """

    def shortest_edit_script(self, a: List[str], b: List[str]) -> Tuple[int, List[Dict[str, Any]]]:
        n: int = len(a)
        m: int = len(b)
        max_d: int = n + m
        v: Dict[int, int] = {1: 0}
        trace: List[Dict[int, int]] = []

        for d in range(max_d + 1):
            trace.append(dict(v))
            for k in range(-d, d + 1, 2):
                if k == -d or (k != d and v.get(k - 1, 0) < v.get(k + 1, 0)):
                    x = v.get(k + 1, 0)
                else:
                    x = v.get(k - 1, 0) + 1

                y = x - k

                while x < n and y < m and a[x] == b[y]:
                    x += 1
                    y += 1

                v[k] = x

                if x >= n and y >= m:
                    script = self._backtrack(trace, a, b, d, n, m)
                    return (d, script)

        return (max_d, [])

    def _backtrack(
        self,
        trace: List[Dict[int, int]],
        a: List[str],
        b: List[str],
        d: int,
        n: int,
        m: int,
    ) -> List[Dict[str, Any]]:
        script: List[Dict[str, Any]] = []
        x: int = n
        y: int = m

        for step in range(d, 0, -1):
            v = trace[step]
            k = x - y

            if k == -step or (k != step and v.get(k - 1, 0) < v.get(k + 1, 0)):
                prev_k = k + 1
            else:
                prev_k = k - 1

            prev_x = v.get(prev_k, 0)
            prev_y = prev_x - prev_k

            while x > prev_x and y > prev_y:
                script.append({"type": "equal", "line": a[x - 1], "old_idx": x - 1, "new_idx": y - 1})
                x -= 1
                y -= 1

            if step > 0:
                if x == prev_x:
                    script.append({"type": "insert", "line": b[prev_y], "new_idx": prev_y})
                elif y == prev_y:
                    script.append({"type": "delete", "line": a[prev_x], "old_idx": prev_x})

            x = prev_x
            y = prev_y

        while x > 0 and y > 0:
            script.append({"type": "equal", "line": a[x - 1], "old_idx": x - 1, "new_idx": y - 1})
            x -= 1
            y -= 1

        script.reverse()
        return script

    def format_unified_hunks(self, script: List[Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for item in script:
            t = item["type"]
            val = item["line"]
            if t == "equal":
                lines.append(f" {val}")
            elif t == "insert":
                lines.append(f"+{val}")
            elif t == "delete":
                lines.append(f"-{val}")
        return lines

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: List[str] = payload.get("source_lines", [])
        target: List[str] = payload.get("target_lines", [])

        if isinstance(source, str):
            source = source.splitlines()
        if isinstance(target, str):
            target = target.splitlines()

        dist, script = self.shortest_edit_script(source, target)
        hunks = self.format_unified_hunks(script)

        return {
            "algorithm": "ALGO-DIFF-146",
            "edit_distance": dist,
            "diff_hunks": hunks,
            "script": script,
        }
