"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STANDARDIZED API RESPONSE ENVELOPE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides the enterprise response envelope mandated by
   `policies/rules/folderStructure/api-request-response-structure.md` (v5.0) and
   `open.standard.md`. Every HTTP REST response returns a standardized envelope:
   - Success: `success: true`, `statusCode: int`, `data: T`, `meta: ResponseMeta`, `errors: null`.
   - Error: `success: false`, `statusCode: int`, `data: null`, `error: ErrorContainer`, `meta: ResponseMeta`, `errors: [...]`.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Envelope models, serialization contracts,
     and error encapsulation conventions are articulated in this header.
   - W3C Trace Context & Correlation: `requestId`, `correlationId`, `trace_id` propagated.
   - ISO-8601 UTC Millisecond Timestamps with literal 'Z'.
   - Uniform Error Taxonomy: Standard error codes mapped to HTTP status codes with retryability.

3. FACTORY HELPERS:
   - build_success_envelope(data, status_code, trace_id, request_id, correlation_id, execution_time_ms, version): Wraps payload in success envelope.
   - build_error_envelope(code, message, status_code, details, retryable, trace_id, request_id, correlation_id, execution_time_ms, version): Wraps error payload.
================================================================================
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str
    rule: Optional[str] = None
    rejectedValue: Optional[Any] = None


class ErrorContainer(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: Optional[List[Dict[str, Any]]] = None


class ResponseMeta(BaseModel):
    requestId: str
    correlationId: str
    causationId: Optional[str] = None
    timestamp: str
    executionTimeMs: int = 0
    apiVersion: str = "v1"
    status: str = "success"
    trace_id: str
    auditLogId: Optional[str] = None
    operationId: Optional[str] = None
    deprecatedFields: Optional[List[str]] = None
    supportedVersions: Optional[List[str]] = None
    staleness: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None
    links: Optional[Dict[str, Any]] = None


class APIResponseEnvelope(BaseModel, Generic[T]):
    success: bool
    statusCode: int
    data: Optional[T] = None
    error: Optional[ErrorContainer] = None
    errors: Optional[List[Dict[str, Any]]] = None
    meta: ResponseMeta


def format_iso_timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def build_success_envelope(
    data: Any,
    status_code: int = 200,
    trace_id: Optional[str] = None,
    request_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    execution_time_ms: int = 0,
    version: str = "v1",
    pagination: Optional[Dict[str, Any]] = None,
    links: Optional[Dict[str, Any]] = None,
    audit_log_id: Optional[str] = None,
) -> Dict[str, Any]:
    current_time = format_iso_timestamp()
    resolved_trace = trace_id or uuid.uuid4().hex
    resolved_req_id = request_id or f"req-{int(time.time()*1000)}-{resolved_trace[:8]}"
    resolved_corr_id = correlation_id or f"corr-{resolved_trace[:12]}"

    return {
        "success": True,
        "statusCode": status_code,
        "data": data,
        "errors": None,
        "meta": {
            "requestId": resolved_req_id,
            "correlationId": resolved_corr_id,
            "causationId": causation_id,
            "timestamp": current_time,
            "executionTimeMs": execution_time_ms,
            "apiVersion": version,
            "status": "success",
            "trace_id": resolved_trace,
            "auditLogId": audit_log_id,
            "operationId": None,
            "deprecatedFields": None,
            "supportedVersions": ["v1"],
            "staleness": None,
            "pagination": pagination,
            "links": links,
        },
    }


def build_error_envelope(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Any] = None,
    retryable: bool = False,
    trace_id: Optional[str] = None,
    request_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    execution_time_ms: int = 0,
    version: str = "v1",
) -> Dict[str, Any]:
    current_time = format_iso_timestamp()
    resolved_trace = trace_id or uuid.uuid4().hex
    resolved_req_id = request_id or f"req-{int(time.time()*1000)}-{resolved_trace[:8]}"
    resolved_corr_id = correlation_id or f"corr-{resolved_trace[:12]}"

    details_list = details if isinstance(details, list) else ([details] if details is not None else None)

    return {
        "success": False,
        "statusCode": status_code,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable,
            "details": details_list,
        },
        "errors": [
            {
                "code": code,
                "message": message,
                "details": details,
            }
        ],
        "meta": {
            "requestId": resolved_req_id,
            "correlationId": resolved_corr_id,
            "causationId": causation_id,
            "timestamp": current_time,
            "executionTimeMs": execution_time_ms,
            "apiVersion": version,
            "status": "error",
            "trace_id": resolved_trace,
            "auditLogId": None,
            "operationId": None,
            "deprecatedFields": None,
            "supportedVersions": ["v1"],
            "staleness": None,
            "pagination": None,
            "links": None,
        },
    }
