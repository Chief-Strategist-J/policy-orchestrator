"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CODE ENGINE ALGORITHM CATALOG LOADER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides dynamic, database/seed-driven contract loading for all Layer 1
   (G1-G6) contracts and G4 Type Adapters. Hardcoded contract dictionaries
   have been removed from this code module and migrated to persistent database
   migrations and canonical seed definitions in `database/migrations/` and
   `database/seeds/algorithm_catalog.json`.

2. SINGLE SOURCE OF TRUTH:
   - Database Migrations: `database/migrations/0002_seed_algorithm_catalog.sql`
   - Database SQLite: `database/migrations/0002_seed_algorithm_catalog_sqlite.sql`
   - Canonical Seed: `database/seeds/algorithm_catalog.json`

3. ZERO INLINE COMMENTS:
   Follows strict architectural zero-inline-comment doctrine.
================================================================================
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    TypeAdapterContract,
)


def _resolve_seed_path() -> Path:
    current_dir = Path(__file__).resolve().parent
    for parent in [current_dir] + list(current_dir.parents):
        candidate = parent / "database" / "seeds" / "algorithm_catalog.json"
        if candidate.exists():
            return candidate
    alt = Path("/home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/database/seeds/algorithm_catalog.json")
    if alt.exists():
        return alt
    raise FileNotFoundError("Canonical algorithm catalog seed file not found in database/seeds/algorithm_catalog.json")


def load_algorithm_contracts(seed_path: Optional[Path] = None) -> List[AlgorithmContract]:
    path = seed_path or _resolve_seed_path()
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    contracts_raw = payload.get("algorithms", [])
    return [AlgorithmContract.from_dict(item) for item in contracts_raw]


def load_type_adapters(seed_path: Optional[Path] = None) -> List[TypeAdapterContract]:
    path = seed_path or _resolve_seed_path()
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    adapters_raw = payload.get("type_adapters", [])
    return [TypeAdapterContract(**item) for item in adapters_raw]


BUILTIN_ALGORITHM_CONTRACTS: List[AlgorithmContract] = load_algorithm_contracts()
BUILTIN_TYPE_ADAPTERS: List[TypeAdapterContract] = load_type_adapters()


def reload_catalog_from_storage(seed_path: Optional[Path] = None) -> None:
    global BUILTIN_ALGORITHM_CONTRACTS, BUILTIN_TYPE_ADAPTERS
    BUILTIN_ALGORITHM_CONTRACTS = load_algorithm_contracts(seed_path)
    BUILTIN_TYPE_ADAPTERS = load_type_adapters(seed_path)
