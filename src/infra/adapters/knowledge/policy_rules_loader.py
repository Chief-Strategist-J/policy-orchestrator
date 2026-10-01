"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: POLICY RULES MARKDOWN KNOWLEDGE LOADER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements KnowledgeSourcePort to scan, parse, and chunk markdown
   policy documents from `policies/rules/` into semantically coherent, grounded
   units for RAG indexing. It preserves section hierarchy, rule headers, and
   file provenance.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Header parsing state machine, regex splitting,
     and category inference algorithms are fully documented in this header block.
   - Heading-Aware Chunking: Chunks are split at Markdown H1/H2/H3 (`#`, `##`, `###`)
     boundaries while preserving the section title and contextual preamble.
   - Deterministic Hashing: IDs are derived from SHA256 of `source_path:heading`.

3. METHOD CONTRACTS:
   - load_all_chunks(): Recursively parses all `.md` files in base directory.
   - load_by_pattern(): Applies glob filtering to locate specific policy subsets.
================================================================================
"""

import os
import re
import hashlib
from typing import List, Dict, Any

from src.domain.ports.knowledge_port import (
    KnowledgeSourcePort,
    KnowledgeChunk,
)

class PolicyRulesMarkdownLoader(KnowledgeSourcePort):
    def __init__(self, base_rules_dir: str) -> None:
        self.base_rules_dir = os.path.abspath(base_rules_dir)

    def _infer_category(self, rel_path: str) -> str:
        parts = rel_path.split(os.sep)
        if len(parts) > 1:
            return parts[0]
        return "general"

    def _chunk_markdown_file(self, file_path: str) -> List[KnowledgeChunk]:
        if not os.path.exists(file_path):
            return []

        rel_path = os.path.relpath(file_path, self.base_rules_dir)
        category = self._infer_category(rel_path)

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        heading_pattern = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)
        splits = heading_pattern.split(content)

        chunks: List[KnowledgeChunk] = []
        current_title = os.path.basename(file_path)
        
        if splits and not splits[0].startswith("#"):
            preamble = splits[0].strip()
            if preamble:
                chunk_id = hashlib.sha256(f"{rel_path}:preamble".encode("utf-8")).hexdigest()[:16]
                chunks.append(
                    KnowledgeChunk(
                        id=chunk_id,
                        source_path=rel_path,
                        section_title=f"{current_title} - Preamble",
                        content=preamble,
                        category=category,
                        metadata={"file": rel_path, "heading_level": 0},
                    )
                )
            splits = splits[1:]

        for i in range(0, len(splits), 2):
            if i + 1 < len(splits):
                raw_heading = splits[i].strip()
                section_body = splits[i + 1].strip()
                heading_clean = re.sub(r"^#{1,4}\s+", "", raw_heading)
                full_content = f"{raw_heading}\n\n{section_body}"
                chunk_id = hashlib.sha256(f"{rel_path}:{heading_clean}".encode("utf-8")).hexdigest()[:16]
                chunks.append(
                    KnowledgeChunk(
                        id=chunk_id,
                        source_path=rel_path,
                        section_title=heading_clean,
                        content=full_content,
                        category=category,
                        metadata={
                            "file": rel_path,
                            "heading": heading_clean,
                            "heading_raw": raw_heading,
                        },
                    )
                )

        return chunks

    def load_all_chunks(self) -> List[KnowledgeChunk]:
        all_chunks: List[KnowledgeChunk] = []
        if not os.path.isdir(self.base_rules_dir):
            return all_chunks

        for root, _, files in os.walk(self.base_rules_dir):
            for file in sorted(files):
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    all_chunks.extend(self._chunk_markdown_file(full_path))

        return all_chunks

    def load_by_pattern(self, pattern: str) -> List[KnowledgeChunk]:
        all_chunks: List[KnowledgeChunk] = []
        if not os.path.isdir(self.base_rules_dir):
            return all_chunks

        regex = re.compile(pattern.replace("*", ".*"))
        for root, _, files in os.walk(self.base_rules_dir):
            for file in sorted(files):
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.base_rules_dir)
                    if regex.search(rel_path):
                        all_chunks.extend(self._chunk_markdown_file(full_path))

        return all_chunks
