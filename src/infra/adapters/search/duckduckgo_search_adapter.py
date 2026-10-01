"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LIVE DUCKDUCKGO / REST SEARCH ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements WebSearchPort using open HTTP search endpoints
   (DuckDuckGo HTML/Instant API or SearXNG instances) to pull real-time CVE,
   RFC, and library documentation without requiring proprietary API keys.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: HTTP request construction, HTML entity
     cleaning, and snippet extraction algorithms are documented in this header.
   - Resilient Fallback: If external network is restricted or offline, returns
     graceful empty response instead of crashing agent reasoning loops.

3. METHOD CONTRACTS:
   - search(): Queries DuckDuckGo API or SearXNG and parses snippet results.
   - fetch_page_content(): Reads text with UTF-8 decode and length capping.
================================================================================
"""

import re
import json
import urllib.parse
import urllib.request
from typing import List, Dict, Any, Optional

from src.domain.ports.search_port import (
    WebSearchPort,
    SearchResultItem,
    SearchResponse,
)

class DuckDuckGoSearchAdapter(WebSearchPort):
    def __init__(self, searxng_url: Optional[str] = None, timeout: int = 10) -> None:
        self.searxng_url = searxng_url.rstrip("/") if searxng_url else None
        self.timeout = timeout

    def _strip_html(self, raw_html: str) -> str:
        clean = re.sub(r"<[^>]+>", " ", raw_html)
        return re.sub(r"\s+", " ", clean).strip()

    def search(self, query: str, top_k: int = 5, domain_filter: Optional[str] = None) -> SearchResponse:
        final_query = f"site:{domain_filter} {query}" if domain_filter else query
        
        if self.searxng_url:
            encoded = urllib.parse.urlencode({"q": final_query, "format": "json"})
            url = f"{self.searxng_url}/search?{encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "policy-agent/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = [
                        SearchResultItem(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            snippet=r.get("content", ""),
                            published_date=r.get("publishedDate"),
                        )
                        for r in data.get("results", [])[:top_k]
                    ]
                    return SearchResponse(query=query, results=results, total_results=len(results), provider="searxng")
            except Exception:
                pass

        encoded = urllib.parse.urlencode({"q": final_query, "format": "json", "no_html": "1", "skip_disambig": "1"})
        url = f"https://api.duckduckgo.com/?{encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "policy-agent/1.0"})
        items: List[SearchResultItem] = []
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("AbstractText"):
                    items.append(
                        SearchResultItem(
                            title=data.get("Heading") or query,
                            url=data.get("AbstractURL") or "https://duckduckgo.com",
                            snippet=data.get("AbstractText"),
                        )
                    )
                for topic in data.get("RelatedTopics", []):
                    if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
                        items.append(
                            SearchResultItem(
                                title=topic.get("Text")[:60],
                                url=topic.get("FirstURL"),
                                snippet=topic.get("Text"),
                            )
                        )
                        if len(items) >= top_k:
                            break
        except Exception:
            items = []

        return SearchResponse(
            query=query,
            results=items[:top_k],
            total_results=len(items[:top_k]),
            provider="duckduckgo",
        )

    def fetch_page_content(self, url: str, max_length: int = 4000) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": "policy-agent/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw_html = resp.read().decode("utf-8", errors="replace")
                return self._strip_html(raw_html)[:max_length]
        except Exception as exc:
            return f"Error fetching content from {url}: {str(exc)}"
