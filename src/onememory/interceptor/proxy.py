"""
OneMemory API Server — REST endpoints for querying and managing memories.

This server is optional. The core flow (mitmproxy addon → files → MCP server)
works without it. This provides REST APIs for dashboards or scripts.
"""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from onememory.brain import create_brain

app = FastAPI(title="OneMemory API")
brain = create_brain()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "onememory", **brain.status()}


@app.get("/api/memories")
async def list_memories(category: str = ""):
    memories = brain.get_all_memories()
    if category:
        memories = [m for m in memories if m.category == category]
    return [m.model_dump() for m in memories]


@app.get("/api/search")
async def search_memories(q: str, limit: int = 10):
    results = brain.search(q, limit)
    return [{"content": r.entry.content, "category": r.entry.category, "score": r.score} for r in results]


@app.get("/api/context")
async def get_context():
    return brain.get_context()


@app.get("/api/recent")
async def recent_conversations(limit: int = 20):
    convos = brain.get_recent_conversations(limit)
    return [c.model_dump() for c in convos]
