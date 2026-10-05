"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: QDRANT VECTOR STORE ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements VectorStorePort for the high-performance open-source
   Qdrant vector engine via its standard HTTP REST API. It handles collection
   initialization, point batch upsert, cosine similarity search, and payload
   filtering without vendor lock-in.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Point conversion, REST request creation,
     payload filter construction, and error extraction are documented in this
     top-side blueprint. Functions and methods remain 100% comment-free.
   - Idempotent Collection Setup: Auto-creates collection if it does not exist.
   - Pure Python HTTP: Uses standard `urllib.request` to avoid SDK coupling.

3. METHOD CONTRACTS:
   - upsert(): PUT `/collections/{collection}/points`
   - query_by_vector(): POST `/collections/{collection}/points/search`
   - delete(): POST `/collections/{collection}/points/delete`
   - count(): POST `/collections/{collection}/points/count`
   - clear(): DELETE `/collections/{collection}` and recreate.
================================================================================
"""

import json
import uuid
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

from src.domain.ports.vector_port import (
    VectorStorePort,
    VectorDocument,
    VectorQueryResult,
)

class QdrantVectorAdapter(VectorStorePort):
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "policy_rules",
        vector_size: int = 1536,
        distance: str = "Cosine",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.url = url.rstrip("/")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        self.api_key = api_key
        self.timeout = timeout
        self._ensure_collection()

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers

    def _request(self, path: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.url}{path}"
        data = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Qdrant HTTP error [{exc.code}] on {method} {path}: {err_body}") from exc
        except Exception as exc:
            raise RuntimeError(f"Qdrant connection error: {str(exc)}") from exc

    def _ensure_collection(self) -> None:
        try:
            self._request(f"/collections/{self.collection_name}", method="GET")
        except Exception:
            try:
                self._request(
                    f"/collections/{self.collection_name}",
                    method="PUT",
                    payload={"vectors": {"size": self.vector_size, "distance": self.distance}},
                )
            except Exception:
                pass

    def _to_uuid(self, doc_id: str) -> str:
        try:
            return str(uuid.UUID(doc_id))
        except ValueError:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))

    def upsert(self, documents: List[VectorDocument]) -> int:
        if not documents:
            return 0
        points = []
        for doc in documents:
            payload = dict(doc.metadata)
            payload["_raw_content"] = doc.content
            payload["_original_id"] = doc.id
            points.append({
                "id": self._to_uuid(doc.id),
                "vector": doc.embedding,
                "payload": payload,
            })
        self._request(f"/collections/{self.collection_name}/points", method="PUT", payload={"points": points})
        return len(points)

    def query_by_vector(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorQueryResult]:
        body: Dict[str, Any] = {
            "vector": vector,
            "limit": top_k,
            "with_payload": True,
            "with_vector": True,
        }
        if filter_metadata:
            must_conditions = [{"key": k, "match": {"value": v}} for k, v in filter_metadata.items()]
            body["filter"] = {"must": must_conditions}

        res = self._request(f"/collections/{self.collection_name}/points/search", method="POST", payload=body)
        points = res.get("result", [])
        results: List[VectorQueryResult] = []

        for p in points:
            payload = p.get("payload", {})
            orig_id = payload.pop("_original_id", str(p.get("id")))
            content = payload.pop("_raw_content", "")
            doc = VectorDocument(
                id=orig_id,
                content=content,
                embedding=p.get("vector") or [],
                metadata=payload,
            )
            results.append(VectorQueryResult(document=doc, score=float(p.get("score", 0.0))))

        return results

    def query_with_quantization(
        self,
        vector: List[float],
        top_k: int = 5,
        rescore: bool = True,
        oversampling: float = 2.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorQueryResult]:
        body: Dict[str, Any] = {
            "vector": vector,
            "limit": top_k,
            "with_payload": True,
            "with_vector": True,
            "params": {
                "quantization": {
                    "ignore": False,
                    "rescore": rescore,
                    "oversampling": oversampling,
                }
            },
        }
        if filter_metadata:
            must_conditions = [{"key": k, "match": {"value": v}} for k, v in filter_metadata.items()]
            body["filter"] = {"must": must_conditions}

        res = self._request(f"/collections/{self.collection_name}/points/search", method="POST", payload=body)
        points = res.get("result", [])
        results: List[VectorQueryResult] = []

        for p in points:
            payload = p.get("payload", {})
            orig_id = payload.pop("_original_id", str(p.get("id")))
            content = payload.pop("_raw_content", "")
            doc = VectorDocument(
                id=orig_id,
                content=content,
                embedding=p.get("vector") or [],
                metadata=payload,
            )
            results.append(VectorQueryResult(document=doc, score=float(p.get("score", 0.0))))

        return results

    def batch_query(
        self,
        vectors: List[List[float]],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorQueryResult]]:
        searches = []
        for vec in vectors:
            search_item: Dict[str, Any] = {
                "vector": vec,
                "limit": top_k,
                "with_payload": True,
                "with_vector": True,
            }
            if filter_metadata:
                search_item["filter"] = {
                    "must": [{"key": k, "match": {"value": v}} for k, v in filter_metadata.items()]
                }
            searches.append(search_item)

        res = self._request(f"/collections/{self.collection_name}/points/search/batch", method="POST", payload={"searches": searches})
        batch_points = res.get("result", [])
        all_results: List[List[VectorQueryResult]] = []

        for points in batch_points:
            item_results: List[VectorQueryResult] = []
            for p in points:
                payload = p.get("payload", {})
                orig_id = payload.pop("_original_id", str(p.get("id")))
                content = payload.pop("_raw_content", "")
                doc = VectorDocument(
                    id=orig_id,
                    content=content,
                    embedding=p.get("vector") or [],
                    metadata=payload,
                )
                item_results.append(VectorQueryResult(document=doc, score=float(p.get("score", 0.0))))
            all_results.append(item_results)

        return all_results

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
        quantization: Optional[Any] = None,
    ) -> bool:
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        payload: Dict[str, Any] = {"vectors": {"size": vector_size, "distance": distance}}
        if quantization:
            if hasattr(quantization, "quantization_type") and quantization.quantization_type == "binary":
                payload["quantization_config"] = {"binary": {"always_ram": getattr(quantization, "always_ram", True)}}
            elif hasattr(quantization, "quantization_type") and quantization.quantization_type == "scalar":
                payload["quantization_config"] = {"scalar": {"type": "int8", "always_ram": getattr(quantization, "always_ram", True)}}
            elif isinstance(quantization, dict):
                payload["quantization_config"] = quantization

        self._request(f"/collections/{collection_name}", method="PUT", payload=payload)
        return True

    def delete(self, ids: List[str]) -> int:
        uuid_ids = [self._to_uuid(i) for i in ids]
        self._request(f"/collections/{self.collection_name}/points/delete", method="POST", payload={"points": uuid_ids})
        return len(ids)

    def count(self) -> int:
        res = self._request(f"/collections/{self.collection_name}/points/count", method="POST", payload={})
        return int(res.get("result", {}).get("count", 0))

    def clear(self) -> None:
        try:
            self._request(f"/collections/{self.collection_name}", method="DELETE")
        except Exception:
            pass
        self._ensure_collection()
