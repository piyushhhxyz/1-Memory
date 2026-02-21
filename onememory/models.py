"""OneMemory data models."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4
from pydantic import BaseModel, Field


class Provider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    UNKNOWN = "unknown"


class Message(BaseModel):
    role: str
    content: str


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    provider: Provider = Provider.UNKNOWN
    model: str = ""
    messages: list[Message] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = Field(default_factory=dict)


class MemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    content: str
    category: str = "general"
    source: str = ""
    tags: list[str] = Field(default_factory=list)
    importance: float = 0.5
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SearchResult(BaseModel):
    entry: MemoryEntry
    score: float


class HippocampusIndex(BaseModel):
    conversations: dict[str, str] = Field(default_factory=dict)
