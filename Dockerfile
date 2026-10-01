# syntax=docker/dockerfile:1.4
# ==============================================================================
# Open-Standard Multi-Stage Dockerfile for Policy Orchestrator & AI Agent
# Adheres strictly to open.standard.md (non-root execution, minimal attack surface)
# ==============================================================================

# Build Stage
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --user .

# Final Distroless/Minimal Runtime Stage
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    POLICY_RULES_DIR="/app/policies/rules" \
    LLM_BACKEND="mock" \
    HOST="0.0.0.0" \
    PORT="8000"

# Create unprivileged non-root user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local

# Copy source code and contracts
COPY --chown=appuser:appgroup src/ /app/src/
COPY --chown=appuser:appgroup contracts/ /app/contracts/
COPY --chown=appuser:appgroup config/ /app/config/
COPY --chown=appuser:appgroup pyproject.toml /app/

# Switch to non-root user
USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

ENTRYPOINT ["python3", "-m", "src.api.cli.main"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
