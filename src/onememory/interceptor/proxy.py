from __future__ import annotations
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from onememory.brain import create_brain
from onememory.models import Conversation, Message, Provider

logger = logging.getLogger("onememory.server")

app = FastAPI(title="OneMemory Server")
brain = create_brain()

# Allow Chrome extension to POST to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CapturePayload(BaseModel):
    provider: str = "openai"
    source: str = "chatgpt-web"
    model: str = ""
    userMessage: str = ""
    assistantContent: str = ""
    timestamp: str = ""


@app.get("/health")
async def health():
    return {"status": "ok", "service": "onememory", **brain.status()}


@app.post("/capture")
async def capture(payload: CapturePayload):
    """Receive a captured conversation from the Chrome extension."""
    messages = []
    if payload.userMessage:
        messages.append(Message(role="user", content=payload.userMessage))
    if payload.assistantContent:
        messages.append(Message(role="assistant", content=payload.assistantContent))

    if not messages:
        return {"status": "skipped", "reason": "no messages"}

    provider = Provider.OPENAI if "openai" in payload.provider.lower() else Provider.ANTHROPIC
    conversation = Conversation(
        provider=provider,
        model=payload.model,
        messages=messages,
        metadata={"source": payload.source},
    )

    cid = brain.capture(conversation)
    logger.info(f"Captured conversation {cid} from {payload.source} ({payload.model})")
    return {"status": "captured", "id": cid, "messages": len(messages)}


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
