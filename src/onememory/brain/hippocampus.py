"""Hippocampus — fast episodic memory capture, like the brain's hippocampus."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from onememory.config import Config
from onememory.models import Conversation, DailyLog
from onememory.brain.repository import FileStore


class Hippocampus:
    """Captures and indexes raw conversations."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.store = FileStore()
        self._on_capture_callbacks: list = []

    def _today_file(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.config.hippocampus_dir / f"{today}.json"

    def _load_daily(self, path: Path) -> DailyLog:
        if path.exists():
            return DailyLog.model_validate_json(path.read_text())
        return DailyLog(date=path.stem)

    def _save_daily(self, path: Path, log: DailyLog) -> None:
        self.store.save(path, log)

    def capture(self, conversation: Conversation) -> str:
        path = self._today_file()
        log = self._load_daily(path)
        log.conversations.append(conversation)
        self._save_daily(path, log)
        for cb in self._on_capture_callbacks:
            try:
                cb(conversation)
            except Exception:
                pass
        return conversation.id

    def get(self, conversation_id: str) -> Conversation | None:
        for path in sorted(self.config.hippocampus_dir.glob("????-??-??.json"), reverse=True):
            log = self._load_daily(path)
            for c in log.conversations:
                if c.id == conversation_id:
                    return c
        return None

    def get_recent(self, limit: int = 20) -> list[Conversation]:
        results: list[Conversation] = []
        for path in sorted(self.config.hippocampus_dir.glob("????-??-??.json"), reverse=True):
            log = self._load_daily(path)
            for c in reversed(log.conversations):
                results.append(c)
                if len(results) >= limit:
                    return results
        return results

    def get_all_today(self) -> list[Conversation]:
        return self._load_daily(self._today_file()).conversations

    def on_capture(self, callback) -> None:
        """Observer pattern — register a callback for new captures."""
        self._on_capture_callbacks.append(callback)

    def count(self) -> int:
        total = 0
        for path in self.config.hippocampus_dir.glob("????-??-??.json"):
            try:
                log = self._load_daily(path)
                total += len(log.conversations)
            except Exception:
                pass
        return total
