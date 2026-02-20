from __future__ import annotations
import json
from onememory.config import Config
from onememory.models import Conversation

HIGH_IMPORTANCE_KEYWORDS = {
    "my name is", "i am", "i'm", "i prefer", "i like", "i love",
    "i hate", "i use", "my favorite", "i work", "i live", "always",
    "never", "important", "remember", "don't forget", "password",
    "key", "secret", "api", "credential", "preference", "style",
    "i want", "i need", "birthday", "email", "phone",
}


class Amygdala:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._scores_path = config.amygdala_dir / "salience.json"

    def _load_scores(self) -> dict[str, float]:
        if self._scores_path.exists():
            return json.loads(self._scores_path.read_text())
        return {}

    def _save_scores(self, scores: dict[str, float]) -> None:
        self._scores_path.parent.mkdir(parents=True, exist_ok=True)
        self._scores_path.write_text(json.dumps(scores, indent=2))

    def score(self, conversation: Conversation) -> float:
        text = " ".join(m.content.lower() for m in conversation.messages)
        base = 0.3
        hits = sum(1 for kw in HIGH_IMPORTANCE_KEYWORDS if kw in text)
        importance = min(1.0, base + hits * 0.1)
        # longer conversations are slightly more important
        msg_bonus = min(0.2, len(conversation.messages) * 0.02)
        importance = min(1.0, importance + msg_bonus)
        scores = self._load_scores()
        scores[conversation.id] = importance
        self._save_scores(scores)
        return importance

    def get_score(self, conversation_id: str) -> float:
        scores = self._load_scores()
        return scores.get(conversation_id, 0.5)
