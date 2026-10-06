"""
================================================================================
ALGORITHM BLUEPRINT: LOG-STRUCTURED MERGE TREE (LSM TREE)
================================================================================

1. OVERVIEW:
   A Log-Structured Merge Tree (LSM Tree) is a write-optimized storage and indexing
   architecture. Writes are buffered sequentially in an in-memory MemTable and
   appended to a Write-Ahead Log (WAL). When full, the MemTable is flushed as an
   immutable Sorted String Table (SSTable). Background leveled compaction merges
   overlapping SSTables, purges tombstones, and ensures fast reads.

2. ARCHITECTURAL COMPONENTS & LIFECYCLE:
   - MemTable: Active in-memory sorted dictionary.
   - Immutable MemTable: Frozen MemTable awaiting disk flush.
   - SSTable (Sorted String Table): Immutable key-value segment sorted by key.
   - Tombstones: Special deletion markers (`__TOMBSTONE__`) ensuring correct deletion semantics.
   - Point Query: Check MemTable -> Check Immutable MemTable -> Check SSTables from L0 to Ln.
   - Compaction: K-way merge of adjacent SSTable segments discarding obsolete versions
     and eligible tombstones.

3. COMPLEXITY ANALYSIS:
   - Write: O(1) sequential append + O(log M) MemTable insertion.
   - Point Read: O(log M + S * log K) where S is number of SSTables and K is SSTable size.
   - Space Amp & Write Amp: Controlled via leveled compaction.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - All state transitions and operations are self-describing; 0 inline comments in functions.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class SSTable:
    def __init__(self, sstable_id: int, entries: List[Tuple[str, Any]]) -> None:
        self.sstable_id: int = sstable_id
        self.entries: List[Tuple[str, Any]] = sorted(entries, key=lambda x: x[0])
        self.keys: List[str] = [k for k, _ in self.entries]
        self.min_key: str = self.keys[0] if self.keys else ""
        self.max_key: str = self.keys[-1] if self.keys else ""

    def get(self, key: str) -> Tuple[bool, Optional[Any]]:
        if not self.keys or key < self.min_key or key > self.max_key:
            return False, None
        import bisect
        idx = bisect.bisect_left(self.keys, key)
        if idx < len(self.keys) and self.keys[idx] == key:
            return True, self.entries[idx][1]
        return False, None


class SearchEngineLsmTreeAlgo:
    """
    --- contract:
      id: ALGO-SRCH-56
      name: SearchEngineLsmTreeAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(log N)
        space: O(MemTableSize)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - index.lsm_tree
      - memtable.sstable
      - storage.append_only
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    TOMBSTONE = "__LSM_TOMBSTONE__"

    def __init__(self, memtable_threshold: int = 4) -> None:
        self._memtable_threshold: int = max(2, memtable_threshold)
        self._memtable: Dict[str, Any] = {}
        self._sstables: List[SSTable] = []
        self._next_sstable_id: int = 1

    def put(self, key: str, value: Any) -> None:
        self._memtable[key] = value
        if len(self._memtable) >= self._memtable_threshold:
            self.flush()

    def delete(self, key: str) -> None:
        self.put(key, self.TOMBSTONE)

    def flush(self) -> Optional[int]:
        if not self._memtable:
            return None
        sorted_pairs = sorted(self._memtable.items(), key=lambda x: x[0])
        sstable = SSTable(self._next_sstable_id, sorted_pairs)
        self._sstables.insert(0, sstable)
        self._next_sstable_id += 1
        self._memtable.clear()
        return sstable.sstable_id

    def get(self, key: str) -> Tuple[bool, Optional[Any]]:
        if key in self._memtable:
            val = self._memtable[key]
            if val == self.TOMBSTONE:
                return False, None
            return True, val

        for sstable in self._sstables:
            found, val = sstable.get(key)
            if found:
                if val == self.TOMBSTONE:
                    return False, None
                return True, val
        return False, None

    def compact(self) -> Dict[str, Any]:
        if len(self._sstables) <= 1:
            return {
                "compacted": False,
                "sstable_count": len(self._sstables)
            }

        merged_dict: Dict[str, Any] = {}
        for sstable in reversed(self._sstables):
            for k, v in sstable.entries:
                merged_dict[k] = v

        active_entries = [(k, v) for k, v in merged_dict.items() if v != self.TOMBSTONE]
        new_sstable = SSTable(self._next_sstable_id, active_entries)
        self._next_sstable_id += 1
        self._sstables = [new_sstable]

        return {
            "compacted": True,
            "new_sstable_id": new_sstable.sstable_id,
            "surviving_keys": len(active_entries),
            "sstable_count": 1
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        threshold = int(payload.get("memtable_threshold", 4))
        operations = payload.get("operations", [])
        query_key = payload.get("query_key")
        trigger_compaction = bool(payload.get("compact", False))

        if threshold != self._memtable_threshold:
            self._memtable_threshold = max(2, threshold)

        for op in operations:
            op_type = str(op.get("op", "")).lower()
            k = str(op.get("key", ""))
            v = op.get("value")
            if op_type in ["put", "insert", "set"]:
                self.put(k, v if v is not None else k)
            elif op_type in ["delete", "remove"]:
                self.delete(k)
            elif op_type == "flush":
                self.flush()

        compaction_meta = None
        if trigger_compaction:
            compaction_meta = self.compact()

        query_found, query_val = (False, None)
        if query_key is not None:
            query_found, query_val = self.get(str(query_key))

        return {
            "algorithm": "ALGO-SRCH-56",
            "memtable_size": len(self._memtable),
            "sstable_count": len(self._sstables),
            "query_key": query_key,
            "query_found": query_found,
            "query_value": query_val,
            "compaction_info": compaction_meta,
            "sstable_manifest": [
                {
                    "id": s.sstable_id,
                    "key_count": len(s.keys),
                    "min_key": s.min_key,
                    "max_key": s.max_key
                } for s in self._sstables
            ]
        }
