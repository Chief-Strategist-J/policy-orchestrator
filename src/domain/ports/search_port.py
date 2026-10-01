"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: WEB SEARCH & LIVE KNOWLEDGE PORT (HEXAGONAL)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port for real-time web search,
   CVE vulnerability lookups, RFC cross-checking, and GitHub repo scraping.
   It enables the AI Agent to dynamically pull verified external knowledge to
   prevent outdated architectural assumptions.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Search query parameters, result encapsulation,
     and rate-limiting policies are articulated in this top blueprint.
   - Grounded External Verification: Results return source title, snippet, URL,
     and fetch timestamp for verifiable citation in decision logs.

3. METHOD CONTRACTS:
   - search(): Executes natural language web search with top-k results.
   - fetch_page_content(): Fetches cleaned text content from an external URL.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class SearchResultItem:
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class SearchResponse:
    query: str
    results: List[SearchResultItem]
    total_results: int
    provider: str

class WebSearchPort(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int = 5, domain_filter: Optional[str] = None) -> SearchResponse:
        pass

    @abstractmethod
    def fetch_page_content(self, url: str, max_length: int = 4000) -> str:
        pass
