"""
Dreamer — Sleep consolidation engine (STUB)

In a full implementation, this would:
1. Read all conversations from hippocampus/today/
2. Call a local LLM (Llama, Kimi 2.5, Qwen, etc.) to extract structured facts
3. Score each fact with the amygdala
4. Store important facts in cortex/
5. Log the consolidation in dreamlog/

For now: extracts basic facts with heuristics (no LLM needed).
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from onememory.config import Config
from onememory.models import MemoryEntry, Conversation
from onememory.brain.hippocampus import Hippocampus
from onememory.brain.cortex import Cortex
from onememory.brain.amygdala import Amygdala


class Dreamer:
    def __init__(self, config: Config, hippocampus: Hippocampus, cortex: Cortex, amygdala: Amygdala) -> None:
        self.config = config
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.amygdala = amygdala

    def dream(self) -> dict:
        """Run consolidation on today's conversations."""
        conversations = self.hippocampus.get_pending()
        if not conversations:
            return {"status": "nothing_to_consolidate", "conversations": 0, "memories_created": 0}

        memories_created = 0
        for convo in conversations:
            score = self.amygdala.score(convo)
            if score >= 0.4:
                extracted = self._extract_facts(convo)
                for fact in extracted:
                    fact.importance = score
                    self.cortex.store_memory(fact)
                    memories_created += 1

        # Write dreamlog
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
        """Simple heuristic fact extraction from conversation messages."""
        facts = []
        for msg in conversation.messages:
            if msg.role != "user":
                continue
            text = msg.content.strip()
            if not text:
                continue
            # Detect identity statements
            lower = text.lower()
            category = "knowledge"
            if any(p in lower for p in ["my name is", "i am a", "i'm a", "i work at", "i work as", "i live in"]):
                category = "identity"
            elif any(p in lower for p in ["i prefer", "i like", "i love", "i hate", "i use", "my favorite", "i always"]):
                category = "preference"

            # Only store statements that look like personal info (not questions or instructions)
            if category != "knowledge" or (len(text.split()) <= 30 and not text.endswith("?")):
                if len(text) > 10:
                    facts.append(MemoryEntry(
                        content=text,
                        category=category,
                        source=f"{conversation.provider}:{conversation.model}",
                        tags=[conversation.provider],
                    ))
        return facts
