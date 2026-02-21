"""Cortex — long-term semantic memory storage using chromadb vector search."""
from __future__ import annotations
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import chromadb
from onememory.config import Config
from onememory.models import MemoryEntry, SearchResult


class Cortex:
    """Stores and searches consolidated memories using vector embeddings."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._db_path = config.cortex_dir / "vectordb"
        self._client = None
        self._collection = None

    def _get_collection(self):
        """Lazy init — recreates client/collection if vectordb was deleted."""
        if self._collection is not None:
            try:
                self._collection.count()
                return self._collection
            except Exception:
                self._client = None
                self._collection = None
        self._client = chromadb.PersistentClient(path=str(self._db_path))
        self._collection = self._client.get_or_create_collection(
            "memories",
            metadata={"hnsw:space": "cosine"},
        )
        return self._collection

    def store_memory(self, entry: MemoryEntry) -> str:
        self._get_collection().upsert(
            ids=[entry.id],
            documents=[entry.content],
            metadatas=[{
                "category": entry.category,
                "source": entry.source,
                "tags": ",".join(entry.tags),
                "importance": entry.importance,
                "timestamp": entry.timestamp,
            }],
        )
        return entry.id

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Semantic vector search via chromadb."""
        collection = self._get_collection()
        count = collection.count()
        if count == 0:
            return []
        result = collection.query(
            query_texts=[query],
            n_results=min(limit, count),
        )
        results = []
        for i, doc_id in enumerate(result["ids"][0]):
            meta = result["metadatas"][0][i]
            distance = result["distances"][0][i] if result.get("distances") else 0
            score = max(0.0, 1.0 - distance)
            entry = MemoryEntry(
                id=doc_id,
                content=result["documents"][0][i],
                category=meta.get("category", "general"),
                source=meta.get("source", ""),
                tags=meta.get("tags", "").split(",") if meta.get("tags") else [],
                importance=meta.get("importance", 0.5),
                timestamp=meta.get("timestamp", ""),
            )
            results.append(SearchResult(entry=entry, score=round(score, 2)))
        return results

    def get_all(self) -> list[MemoryEntry]:
        collection = self._get_collection()
        count = collection.count()
        if count == 0:
            return []
        result = collection.get()
        entries = []
        for i, doc_id in enumerate(result["ids"]):
            meta = result["metadatas"][i]
            entries.append(MemoryEntry(
                id=doc_id,
                content=result["documents"][i],
                category=meta.get("category", "general"),
                source=meta.get("source", ""),
                tags=meta.get("tags", "").split(",") if meta.get("tags") else [],
                importance=meta.get("importance", 0.5),
                timestamp=meta.get("timestamp", ""),
            ))
        return entries

    def get_by_category(self, category: str) -> list[MemoryEntry]:
        collection = self._get_collection()
        count = collection.count()
        if count == 0:
            return []
        result = collection.get(where={"category": category})
        entries = []
        for i, doc_id in enumerate(result["ids"]):
            meta = result["metadatas"][i]
            entries.append(MemoryEntry(
                id=doc_id,
                content=result["documents"][i],
                category=meta.get("category", "general"),
                source=meta.get("source", ""),
                tags=meta.get("tags", "").split(",") if meta.get("tags") else [],
                importance=meta.get("importance", 0.5),
                timestamp=meta.get("timestamp", ""),
            ))
        return entries

    def count(self) -> int:
        return self._get_collection().count()
