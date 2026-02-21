"""
mitmproxy addon — intercepts ChatGPT web conversations and saves to OneMemory.

Listens for POST requests to chatgpt.com's conversation endpoint,
parses the v1 delta-encoded SSE response, and saves both user message
and assistant reply to ~/.onememory/hippocampus/.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from mitmproxy import http

ONEMEMORY_DIR = Path.home() / ".onememory"
HIPPOCAMPUS_DIR = ONEMEMORY_DIR / "hippocampus"


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def _is_chatgpt_conversation(flow: http.HTTPFlow) -> bool:
    """Match POST to chatgpt.com/.../f/conversation (the chat endpoint)."""
    if flow.request.method != "POST":
        return False
    if "chatgpt.com" not in flow.request.pretty_host:
        return False
    path = flow.request.path.split("?")[0].rstrip("/")
    return path.endswith("/f/conversation")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def _extract_user_message(request_body: dict) -> str:
    """Pull the user's message text from the ChatGPT request payload."""
    for msg in reversed(request_body.get("messages", [])):
        if not isinstance(msg, dict):
            continue
        author = msg.get("author", {})
        role = author.get("role", "") if isinstance(author, dict) else str(author)
        if role != "user":
            continue
        content = msg.get("content", "")
        if isinstance(content, dict):
            parts = content.get("parts", [])
            return " ".join(p for p in parts if isinstance(p, str))
        elif isinstance(content, str):
            return content
    return ""


def _extract_assistant_response(raw: str) -> tuple[str, str]:
    """
    Parse ChatGPT's v1 delta-encoded SSE stream.

    Text chunks arrive as patch arrays:
        data: {"v": [{"p": "/message/content/parts/0", "o": "append", "v": "Hello"}, ...]}

    Full messages (for model slug extraction):
        data: {"v": {"message": {..., "metadata": {"model_slug": "gpt-4o"}}}}
    """
    appended_text: list[str] = []
    model = ""

    for line in raw.split("\n"):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        data_str = line[6:].strip()
        if data_str == "[DONE]":
            break
        try:
            data = json.loads(data_str)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue

        v = data.get("v")

        # Patch array — collect text appends
        if isinstance(v, list):
            for patch in v:
                if not isinstance(patch, dict):
                    continue
                if (
                    patch.get("o") == "append"
                    and isinstance(patch.get("v"), str)
                    and "content/parts" in patch.get("p", "")
                ):
                    appended_text.append(patch["v"])

        # Full message dict — extract model slug
        elif isinstance(v, dict):
            msg = v.get("message")
            if isinstance(msg, dict):
                meta = msg.get("metadata", {})
                if isinstance(meta, dict):
                    slug = meta.get("model_slug") or meta.get("resolved_model_slug", "")
                    if slug:
                        model = slug

    return "".join(appended_text), model


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def _save_conversation(user_message: str, assistant_message: str, model: str) -> Path:
    """Write a conversation JSON to hippocampus and update the index."""
    conv_id = datetime.now(timezone.utc).strftime("%H%M%S%f")[:12]
    conversation = {
        "id": conv_id,
        "provider": "openai",
        "model": model or "chatgpt",
        "messages": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"source": "chatgpt-web"},
    }
    if user_message:
        conversation["messages"].append({"role": "user", "content": user_message})
    if assistant_message:
        conversation["messages"].append({"role": "assistant", "content": assistant_message})

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_dir = HIPPOCAMPUS_DIR / today
    today_dir.mkdir(parents=True, exist_ok=True)
    filepath = today_dir / f"{conv_id}.json"
    filepath.write_text(json.dumps(conversation, indent=2))

    index_path = HIPPOCAMPUS_DIR / "index.json"
    index = {"conversations": {}}
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text())
        except Exception:
            pass
    index["conversations"][conv_id] = str(filepath)
    index_path.write_text(json.dumps(index, indent=2))

    return filepath


# ---------------------------------------------------------------------------
# Addon
# ---------------------------------------------------------------------------

class OneMemoryAddon:

    def __init__(self):
        HIPPOCAMPUS_DIR.mkdir(parents=True, exist_ok=True)
        (ONEMEMORY_DIR / "cortex" / "knowledge").mkdir(parents=True, exist_ok=True)
        (ONEMEMORY_DIR / "amygdala").mkdir(parents=True, exist_ok=True)
        print("[OneMemory] Listening for ChatGPT conversations...")

    def requestheaders(self, flow: http.HTTPFlow) -> None:
        """Suppress non-ChatGPT traffic from mitmproxy logs."""
        if "chatgpt.com" not in flow.request.pretty_host:
            flow.request.is_replay = True

    def responseheaders(self, flow: http.HTTPFlow) -> None:
        """Buffer full SSE response instead of streaming through."""
        if _is_chatgpt_conversation(flow):
            flow.response.stream = False

    def response(self, flow: http.HTTPFlow) -> None:
        if not _is_chatgpt_conversation(flow):
            return

        try:
            req_body = json.loads(flow.request.get_text() or "{}")
            resp_text = flow.response.get_text() or ""

            user_message = _extract_user_message(req_body)
            assistant_message, model = _extract_assistant_response(resp_text)

            if not user_message and not assistant_message:
                return

            filepath = _save_conversation(user_message, assistant_message, model)
            print(f"[OneMemory] Captured ({model}): {user_message[:60]}")
            print(f"[OneMemory] Reply: {assistant_message[:60]}")
            print(f"[OneMemory] Saved: {filepath}")
        except Exception as e:
            print(f"[OneMemory] Error: {e}")


addons = [OneMemoryAddon()]
