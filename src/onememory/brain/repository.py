"""File-based storage — the Repository pattern for OneMemory."""
from __future__ import annotations
import json
from pathlib import Path
from pydantic import BaseModel


class FileStore:
    """Simple JSON file store. All memory persistence goes through here."""

    def save(self, path: Path, data: BaseModel) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data.model_dump_json(indent=2))

    def load(self, path: Path, model_cls: type[BaseModel]) -> BaseModel:
        return model_cls.model_validate_json(path.read_text())

    def list_files(self, directory: Path, pattern: str = "*.json") -> list[Path]:
        if not directory.exists():
            return []
        return sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

    def delete(self, path: Path) -> None:
        if path.exists():
            path.unlink()
