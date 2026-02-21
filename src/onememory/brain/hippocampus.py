"""Hippocampus — fast episodic memory capture, like the brain's hippocampus."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from onememory.config import Config
from onememory.models import Conversation, HippocampusIndex
from onememory.brain.repository import FileStore


class Hippocampus:
    """Captures and indexes raw conversations."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.store = FileStore()
        self._on_capture_callbacks: list = []

    @property
    def _index_path(self) -> Path:
        return self.config.hippocampus_dir / "index.json"

    def _load_index(self) -> HippocampusIndex:
        if self._index_path.exists():
            return HippocampusIndex.model_validate_json(self._index_path.read_text())
        return HippocampusIndex()

    def _save_index(self, index: HippocampusIndex) -> None:
        self.store.save(self._index_path, index)

    def _today_dir(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        d = self.config.hippocampus_dir / today
        d.mkdir(parents=True, exist_ok=True)
        return d

    def capture(self, conversation: Conversation) -> str:
        filepath = self._today_dir() / f"{conversation.id}.json"
        self.store.save(filepath, conversation)
        index = self._load_index()
        index.conversations[conversation.id] = str(filepath)
        self._save_index(index)
        for cb in self._on_capture_callbacks:
            try:
                cb(conversation)
            except Exception:
                pass
        return conversation.id

    def get(self, conversation_id: str) -> Conversation | None:
        index = self._load_index()
        filepath = index.conversations.get(conversation_id)
        if filepath and Path(filepath).exists():
            return Conversation.model_validate_json(Path(filepath).read_text())
        return None

    def get_recent(self, limit: int = 20) -> list[Conversation]:
        index = self._load_index()
        results = []
        for cid in list(index.conversations.keys())[-limit:]:
            c = self.get(cid)
            if c:
                results.append(c)
        return results

    def get_all_today(self) -> list[Conversation]:
        results = []
        for f in sorted(self._today_dir().glob("*.json")):
            try:
                results.append(Conversation.model_validate_json(f.read_text()))
            except Exception:
                pass
        return results

    def on_capture(self, callback) -> None:
        """Observer pattern — register a callback for new captures."""
        self._on_capture_callbacks.append(callback)

    def count(self) -> int:
        return len(self._load_index().conversations)
