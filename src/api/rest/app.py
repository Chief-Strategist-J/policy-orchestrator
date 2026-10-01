"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FASTAPI APPLICATION FACTORY
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module constructs the ASGI FastAPI application instance. It mounts
   the OpenTelemetry tracing context middleware, global error interceptors,
   CORS handlers, and versioned API routers.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Middleware execution order, error response
     envelopes, and application lifecycle events are documented in this header.
   - Global Error Handler: Any uncaught exception is caught and serialized into
     the standardized `{meta, data, errors}` envelope with HTTP 500.
================================================================================
"""

import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.rest.v1.router import router as v1_router
from src.api.rest.envelope import build_error_envelope

def create_app() -> FastAPI:
    app = FastAPI(
        title="Policy Orchestrator API",
        description="Repository Invariant Auditor, Policy Synchronizer, and AI Policy Agent",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_context_middleware(request: Request, call_next):
        trace_id = request.headers.get("x-trace-id") or request.headers.get("traceparent") or uuid.uuid4().hex
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["x-trace-id"] = trace_id
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
        err_envelope = build_error_envelope(
            code="INTERNAL_SERVER_ERROR",
            message=str(exc),
            trace_id=trace_id,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=err_envelope,
        )

    app.include_router(v1_router)

    return app

app = create_app()
