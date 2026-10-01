"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MOCK / OFFLINE WEB SEARCH ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides a deterministic, zero-network implementation of
   WebSearchPort. It returns synthetic search findings and mock RFC/CVE documents
   for local testing, offline policy checks, and CI/CD pipelines.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Mock dispatch rules and synthetic document
     payloads are declared in this top header block.
================================================================================
"""

from typing import List, Dict, Any, Optional

from src.domain.ports.search_port import (
    WebSearchPort,
    SearchResultItem,
    SearchResponse,
)

class MockWebSearchAdapter(WebSearchPort):
    def search(self, query: str, top_k: int = 5, domain_filter: Optional[str] = None) -> SearchResponse:
        results = [
            SearchResultItem(
                title=f"RFC / Standard for: {query[:40]}",
                url="https://standards.open.org/rfc/w3c-trace-context",
                snippet=f"Official specifications and best practices regarding {query}. Mandates W3C traceparent headers and CloudEvents 1.0.",
                published_date="2026-01-01",
            ),
            SearchResultItem(
                title=f"Security Best Practices & Invariants ({query[:30]})",
                url="https://cve.mitre.org/guidelines",
                snippet="Guidelines for tenant data isolation, zero inline comments in core logic, and atomic transactional outbox patterns.",
                published_date="2026-05-15",
            ),
        ]
        return SearchResponse(
            query=query,
            results=results[:top_k],
            total_results=len(results[:top_k]),
            provider="mock-search",
        )

    def fetch_page_content(self, url: str, max_length: int = 4000) -> str:
        return f"[Mock Page Content for {url}]\nOpen standards, W3C traceparent context, and CloudEvents specification."
