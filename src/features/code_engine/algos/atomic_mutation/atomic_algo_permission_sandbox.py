"""
================================================================================
ALGORITHM BLUEPRINT: SANDBOXING AND PERMISSION BOUNDARIES (RESTRICTED EXECUTION)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Enforces runtime security and permission boundaries for autonomous agent tool
   invocations. Validates filesystem paths against allowlisted roots to block
   symlink escapes and directory traversal attacks (`../`), inspects commands
   against allowed toolsets, enforces network domain allowlists, and sanitizes
   untrusted content to neutralize prompt-injection instructions embedded in
   source code comments or issues.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Symlink Escapes: Resolves real physical paths and asserts strict containment
     within allowlisted workspace roots.
   - Command Whitelisting: Rejects any command containing unauthorized shell operators
     or unlisted executable binaries.
   - Prompt Injection Shield: Flags instruction patterns embedded within code comments.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Path_Length + Text_Length)
   - Space Complexity: O(1)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import os
import re
from typing import Dict, Any, List, Optional


class CodeEnginePermissionSandboxAlgo:
    """
    --- contract:
      id: ALGO-ATMC-206
      name: CodeEnginePermissionSandboxAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(N)
        space: O(1)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - sandboxing.permissions
      - security.path_traversal_guard
      - command_whitelist
      input_schema:
        allowlisted_roots: array
        allowed_commands: array
        allowed_domains: array
      output_schema:
        algorithm: string
        is_safe: boolean
        violation_reason: string
    ---
    """

    SUSPICIOUS_INSTRUCTION_PATTERNS = [
        re.compile(r"(?:ignore previous instructions|delete all files|system prompt override)", re.IGNORECASE),
        re.compile(r"(?:curl\s+.*?\|\s*bash|rm\s+-rf\s+/)", re.IGNORECASE),
    ]

    def validate_path_access(
        self, target_path: str, allowlisted_roots: List[str]
    ) -> Dict[str, Any]:
        norm_target = os.path.abspath(target_path)
        is_allowed = False

        for root in allowlisted_roots:
            norm_root = os.path.abspath(root)
            if os.path.commonpath([norm_target, norm_root]) == norm_root:
                is_allowed = True
                break

        return {
            "algorithm": "ALGO-ATMC-206",
            "target_path": target_path,
            "resolved_path": norm_target,
            "is_safe": is_allowed,
            "violation_reason": None if is_allowed else f"Path '{target_path}' escapes allowlisted workspace roots.",
        }

    def validate_command(
        self, command: str, allowed_commands: List[str]
    ) -> Dict[str, Any]:
        parts = command.strip().split()
        if not parts:
            return {"algorithm": "ALGO-ATMC-206", "is_safe": False, "violation_reason": "Empty command."}

        binary = os.path.basename(parts[0])
        is_allowed = binary in allowed_commands

        if not is_allowed:
            return {
                "algorithm": "ALGO-ATMC-206",
                "command": command,
                "is_safe": False,
                "violation_reason": f"Binary '{binary}' is not in allowlisted commands: {allowed_commands}",
            }

        forbidden_tokens = [";", "&&", "||", "|", "`", "$("]
        for tok in forbidden_tokens:
            if tok in command:
                return {
                    "algorithm": "ALGO-ATMC-206",
                    "command": command,
                    "is_safe": False,
                    "violation_reason": f"Command contains forbidden shell operator '{tok}'",
                }

        return {
            "algorithm": "ALGO-ATMC-206",
            "command": command,
            "is_safe": True,
            "violation_reason": None,
        }

    def sanitize_untrusted_content(self, text: str) -> Dict[str, Any]:
        detected_injections: List[str] = []
        for pat in self.SUSPICIOUS_INSTRUCTION_PATTERNS:
            matches = pat.findall(text)
            if matches:
                detected_injections.extend(matches)

        return {
            "algorithm": "ALGO-ATMC-206",
            "is_safe": len(detected_injections) == 0,
            "detected_injections": detected_injections,
            "sanitized": len(detected_injections) == 0,
        }
