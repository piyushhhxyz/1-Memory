"""
Dreamer — sleep consolidation engine.

Reads today's conversations from hippocampus, extracts structured facts
using heuristics, scores them, and stores important ones in cortex.

In a full implementation this would use a local LLM (Llama, Qwen, etc.)
for smarter extraction. For now: keyword-based heuristics.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from onememory.config import Config
from onememory.models import MemoryEntry, Conversation
from onememory.brain.hippocampus import Hippocampus
from onememory.brain.cortex import Cortex
from onememory.brain.amygdala import Amygdala

IDENTITY_SIGNALS = ["my name is", "i am a", "i'm a", "i work at", "i work as", "i live in"]
PREFERENCE_SIGNALS = ["i prefer", "i like", "i love", "i hate", "i use", "my favorite", "i always"]


class Dreamer:
    def __init__(self, config: Config, hippocampus: Hippocampus, cortex: Cortex, amygdala: Amygdala) -> None:
        self.config = config
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.amygdala = amygdala

    def dream(self) -> dict:
        """Run consolidation on today's conversations."""
        conversations = self.hippocampus.get_all_today()
        if not conversations:
            return {"status": "nothing_to_consolidate", "conversations": 0, "memories_created": 0}

        memories_created = 0
        for convo in conversations:
            score = self.amygdala.score(convo)
            if score >= 0.4:
                for fact in self._extract_facts(convo):
                    fact.importance = score
                    self.cortex.store_memory(fact)
                    memories_created += 1

        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conversations_processed": len(conversations),
            "memories_created": memories_created,
        }
        log_path = self.config.dreamlog_dir / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(log, indent=2))

        return {"status": "done", "conversations": len(conversations), "memories_created": memories_created}

    def _extract_facts(self, conversation: Conversation) -> list[MemoryEntry]:
        facts = []
        for msg in conversation.messages:
            if msg.role != "user":
                continue
            text = msg.content.strip()
            if not text or len(text) < 10:
                continue

            lower = text.lower()
            category = "knowledge"
            if any(sig in lower for sig in IDENTITY_SIGNALS):
                category = "identity"
            elif any(sig in lower for sig in PREFERENCE_SIGNALS):
                category = "preference"

            if category != "knowledge" or (len(text.split()) <= 30 and not text.endswith("?")):
                facts.append(MemoryEntry(
                    content=text,
                    category=category,
                    source=f"{conversation.provider}:{conversation.model}",
                    tags=[conversation.provider],
                ))
        return facts
