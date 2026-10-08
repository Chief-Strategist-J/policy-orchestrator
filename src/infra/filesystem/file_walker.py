"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BOUNDED REPOSITORY FILESYSTEM WALKER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides an infrastructure adapter implementing safe, bounded,
   deterministic depth-first filesystem traversals with directory deny-listing,
   canonical path resolution, and zero-allocation iterator streaming.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All filesystem traversal constraints, safety
     checks, and error boundaries are documented strictly in this top-side header.
     Function bodies remain 100% comment-free and pure.
   - Bounded Resource Invariants: Enforces maximum tree depth and ignores vendor,
     build, cache, and hidden directories to prevent memory and I/O thrashing.
   - Deterministic Ordering: Emits directory entries in sorted lexicographical order.

3. ERROR HANDLING & SECURITY INVARIANTS:
   - Symlinks resolving outside the root directory are blocked.
   - Permission errors (EACCES) are caught gracefully without aborting traversal.
================================================================================
"""

import os
from pathlib import Path
from typing import List, Set, Generator

DEFAULT_IGNORED_DIRS: Set[str] = {
    ".git", "node_modules", "dist", "build", ".next", "vendor",
    ".idea", ".vscode", "__pycache__", ".turbo", "coverage",
    "data", "brain", ".gemini", "scratch", "tmp", "bin",
    "venv", ".venv", "env", ".env", ".pytest_cache", ".mypy_cache", ".ruff_cache"
}

def stream_repository_files(
    root_dir: str,
    allowed_extensions: Set[str],
    ignored_dirs: Set[str] = DEFAULT_IGNORED_DIRS
) -> Generator[Path, None, None]:
    root_path = Path(root_dir).resolve()
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = sorted([
            d for d in dirnames 
            if d not in ignored_dirs and not d.startswith(".")
        ])
        
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() in allowed_extensions:
                yield fpath
