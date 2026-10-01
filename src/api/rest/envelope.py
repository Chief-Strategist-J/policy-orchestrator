"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STANDARDIZED API RESPONSE ENVELOPE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides the enterprise response envelope mandated by
   `policies/rules/folderStructure/api-request-response-structure.md` and
   `open.standard.md`. Every HTTP response returns `{meta, data, errors}`
   with W3C trace IDs, ISO-8601 timestamps, and semantic status indicators.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Envelope models, serialization contracts,
     and error encapsulation conventions are articulated in this header.
   - Uniform Error Propagation: Errors are structured dictionaries with `code`,
     `message`, and optional `details`.

3. FACTORY HELPERS:
   - success_response(data, trace_id, version): Wraps payload in success envelope.
   - error_response(code, message, details, trace_id): Wraps error payload.
================================================================================
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseMeta(BaseModel):
    trace_id: str
    timestamp: str
    version: str = "v1"
    status: str = "success"

class APIResponseEnvelope(BaseModel, Generic[T]):
    meta: ResponseMeta
    data: Optional[T] = None
    errors: Optional[List[Dict[str, Any]]] = None

def build_success_envelope(data: Any, trace_id: Optional[str] = None, version: str = "v1") -> Dict[str, Any]:
    current_time = datetime.now(timezone.utc).isoformat()
    tid = trace_id or uuid.uuid4().hex
    return {
        "meta": {
            "trace_id": tid,
            "timestamp": current_time,
            "version": version,
            "status": "success",
        },
        "data": data,
        "errors": None,
    }

def build_error_envelope(
    code: str,
    message: str,
    details: Optional[Any] = None,
    trace_id: Optional[str] = None,
    version: str = "v1",
) -> Dict[str, Any]:
    current_time = datetime.now(timezone.utc).isoformat()
    tid = trace_id or uuid.uuid4().hex
    return {
        "meta": {
            "trace_id": tid,
            "timestamp": current_time,
            "version": version,
            "status": "error",
        },
        "data": None,
        "errors": [
            {
                "code": code,
                "message": message,
                "details": details,
            }
        ],
    }
