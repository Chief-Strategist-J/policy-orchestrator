"""
================================================================================
ALGORITHM BLUEPRINT: LANGUAGE SERVER PROTOCOL (LSP) JSON-RPC ENGINE
================================================================================

1. OVERVIEW:
   Language Server Protocol (LSP) standardizes code intelligence interactions
   between client editors/agents and language analysis servers via JSON-RPC 2.0.
   Handles capabilities negotiation (`initialize`), document synchronization (`didOpen`,
   `didChange`), symbol requests (`definition`, `references`, `rename`), and diagnostic
   validation (`publishDiagnostics`) without executing ad-hoc IDE scripts.

2. PROTOCOL METHOD MATRIX:
   - `initialize`: Client capabilities handshake.
   - `textDocument/definition`: Resolves identifier to URI and Range [start, end].
   - `textDocument/references`: Finds all call and usage ranges across workspace.
   - `textDocument/rename`: Returns a `WorkspaceEdit` describing multi-file diffs.
   - `textDocument/publishDiagnostics`: Push notifications for errors and warnings.

3. COMPLEXITY ANALYSIS:
   - Request Marshalling: O(1).
   - Diagnostic Parsing: O(D) where D is diagnostic count.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional


class SearchEngineLspProtocolAlgo:
    """
    Implements Language Server Protocol (LSP) JSON-RPC message construction and response parsing.
    """

    def build_request(self, method: str, params: Dict[str, Any], request_id: int = 1) -> Dict[str, Any]:
        """
        Constructs a standard LSP JSON-RPC 2.0 request payload.
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }

    def build_definition_request(self, uri: str, line: int, character: int, request_id: int = 1) -> Dict[str, Any]:
        return self.build_request(
            "textDocument/definition",
            {
                "textDocument": {"uri": uri},
                "position": {"line": line, "character": character}
            },
            request_id=request_id
        )

    def build_references_request(self, uri: str, line: int, character: int, include_decl: bool = True, request_id: int = 2) -> Dict[str, Any]:
        return self.build_request(
            "textDocument/references",
            {
                "textDocument": {"uri": uri},
                "position": {"line": line, "character": character},
                "context": {"includeDeclaration": include_decl}
            },
            request_id=request_id
        )

    def build_rename_request(self, uri: str, line: int, character: int, new_name: str, request_id: int = 3) -> Dict[str, Any]:
        return self.build_request(
            "textDocument/rename",
            {
                "textDocument": {"uri": uri},
                "position": {"line": line, "character": character},
                "newName": new_name
            },
            request_id=request_id
        )

    def parse_diagnostics(self, notification_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts errors and warnings from a publishDiagnostics notification.
        """
        params = notification_payload.get("params", {})
        uri = params.get("uri", "")
        diagnostics = params.get("diagnostics", [])

        parsed: List[Dict[str, Any]] = []
        for diag in diagnostics:
            severity_num = diag.get("severity", 1)
            severity = "ERROR" if severity_num == 1 else "WARNING" if severity_num == 2 else "INFO"
            parsed.append({
                "uri": uri,
                "message": diag.get("message", ""),
                "severity": severity,
                "range": diag.get("range", {}),
                "source": diag.get("source", "lsp_server")
            })
        return parsed

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes LSP message generation and diagnostic parsing.
        """
        action = str(payload.get("action", "build_definition")).lower()
        uri = str(payload.get("uri", "file:///workspace/main.py"))
        line = int(payload.get("line", 10))
        character = int(payload.get("character", 5))
        new_name = payload.get("new_name")
        diag_payload = payload.get("diagnostic_payload")

        lsp_message = None
        parsed_diags = []

        if action == "build_definition":
            lsp_message = self.build_definition_request(uri, line, character)
        elif action == "build_references":
            lsp_message = self.build_references_request(uri, line, character)
        elif action == "build_rename" and new_name:
            lsp_message = self.build_rename_request(uri, line, character, str(new_name))
        elif action == "parse_diagnostics" and diag_payload:
            parsed_diags = self.parse_diagnostics(diag_payload)

        return {
            "algorithm": "ALGO-SRCH-90",
            "action": action,
            "lsp_message": lsp_message,
            "diagnostics": parsed_diags,
            "diagnostic_count": len(parsed_diags)
        }
