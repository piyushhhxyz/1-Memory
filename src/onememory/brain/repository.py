from __future__ import annotations
import json
from pathlib import Path
from typing import Protocol, runtime_checkable
from pydantic import BaseModel


@runtime_checkable
class MemoryStore(Protocol):
    def save(self, path: Path, data: BaseModel) -> None: ...
    def load(self, path: Path, model_cls: type[BaseModel]) -> BaseModel: ...
    def list_files(self, directory: Path, pattern: str) -> list[Path]: ...
    def delete(self, path: Path) -> None: ...


class FileStore:
    def save(self, path: Path, data: BaseModel) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data.model_dump_json(indent=2))

    def load(self, path: Path, model_cls: type[BaseModel]) -> BaseModel:
        return model_cls.model_validate_json(path.read_text())

    def load_raw(self, path: Path) -> dict:
        return json.loads(path.read_text())

    def save_raw(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    def list_files(self, directory: Path, pattern: str = "*.json") -> list[Path]:
        if not directory.exists():
            return []
        return sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

    def delete(self, path: Path) -> None:
        if path.exists():
            path.unlink()

    def save_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def load_text(self, path: Path) -> str:
        return path.read_text()
