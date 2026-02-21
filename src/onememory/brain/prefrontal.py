"""Prefrontal Cortex — the query orchestrator (Facade pattern)."""
from __future__ import annotations
from onememory.config import Config
from onememory.models import Conversation, MemoryEntry, SearchResult
from onememory.brain.hippocampus import Hippocampus
from onememory.brain.cortex import Cortex
from onememory.brain.amygdala import Amygdala


class PrefrontalCortex:
    """Single entry point for all memory operations."""

    def __init__(self, config: Config, hippocampus: Hippocampus, cortex: Cortex, amygdala: Amygdala) -> None:
        self.config = config
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.amygdala = amygdala
        self.hippocampus.on_capture(self.amygdala.score)

    def capture(self, conversation: Conversation) -> str:
        return self.hippocampus.capture(conversation)

    def remember(self, content: str, category: str = "general", tags: list[str] | None = None) -> str:
        entry = MemoryEntry(content=content, category=category, tags=tags or [], importance=0.7, source="manual")
        return self.cortex.store_memory(entry)

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        return self.cortex.search(query, limit)

    def get_recent_conversations(self, limit: int = 20) -> list[Conversation]:
        return self.hippocampus.get_recent(limit)

    def get_context(self) -> dict:
        memories = self.cortex.get_all()
        recent = self.hippocampus.get_recent(5)
        identity = [m for m in memories if m.category == "identity"]
        preferences = [m for m in memories if m.category == "preference"]
        knowledge = [m for m in memories if m.category not in ("identity", "preference")]
        return {
            "identity": [m.content for m in identity],
            "preferences": [m.content for m in preferences],
            "knowledge": [m.content for m in knowledge],
            "recent_conversations": len(recent),
            "total_memories": len(memories),
            "total_conversations": self.hippocampus.count(),
        }

    def get_all_memories(self) -> list[MemoryEntry]:
        return self.cortex.get_all()

    def status(self) -> dict:
        return {
            "conversations_captured": self.hippocampus.count(),
            "memories_stored": self.cortex.count(),
            "memory_dir": str(self.config.base_dir),
        }
