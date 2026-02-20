from __future__ import annotations
from onememory.config import Config
from onememory.models import MemoryEntry, SearchResult
from onememory.brain.repository import FileStore


class Cortex:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.store = FileStore()

    def store_memory(self, entry: MemoryEntry) -> str:
        if entry.category in ("identity", "preference", "preferences"):
            directory = self.config.cortex_dir
        else:
            directory = self.config.cortex_dir / "knowledge"
        filepath = directory / f"{entry.id}.json"
        self.store.save(filepath, entry)
        return entry.id

    def get(self, memory_id: str) -> MemoryEntry | None:
        for pattern in ["*.json", "knowledge/*.json"]:
            for f in self.config.cortex_dir.glob(pattern):
                if f.stem == memory_id:
                    return MemoryEntry.model_validate_json(f.read_text())
        return None

    def get_all(self) -> list[MemoryEntry]:
        results = []
        for f in self.store.list_files(self.config.cortex_dir, "*.json"):
            try:
                results.append(MemoryEntry.model_validate_json(f.read_text()))
            except Exception:
                pass
        for f in self.store.list_files(self.config.cortex_dir / "knowledge", "*.json"):
            try:
                results.append(MemoryEntry.model_validate_json(f.read_text()))
            except Exception:
                pass
        return results

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        query_tokens = set(query.lower().split())
        if not query_tokens:
            return []
        results = []
        for entry in self.get_all():
            content_tokens = set(entry.content.lower().split())
            tag_tokens = {t.lower() for t in entry.tags}
            all_tokens = content_tokens | tag_tokens | {entry.category.lower()}
            overlap = query_tokens & all_tokens
            if overlap:
                score = len(overlap) / len(query_tokens) * entry.importance
                results.append(SearchResult(entry=entry, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def get_by_category(self, category: str) -> list[MemoryEntry]:
        return [e for e in self.get_all() if e.category == category]

    def count(self) -> int:
        return len(self.get_all())
