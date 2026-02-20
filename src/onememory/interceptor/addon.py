"""
mitmproxy addon — intercepts ChatGPT conversations and saves to OneMemory.

Usage:
    mitmdump -s addon.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# mitmproxy imports
from mitmproxy import http

# We write directly to disk (no server dependency) to keep it lean.
# The brain modules are imported inline to avoid mitmproxy env conflicts.

ONEMEMORY_DIR = Path.home() / ".onememory"
HIPPOCAMPUS_DIR = ONEMEMORY_DIR / "hippocampus"
CHATGPT_CONVERSATION_PATH = "/backend-api/conversation"


class OneMemoryAddon:
    """Captures ChatGPT web conversations via mitmproxy."""

    def __init__(self):
        HIPPOCAMPUS_DIR.mkdir(parents=True, exist_ok=True)
        (ONEMEMORY_DIR / "cortex" / "knowledge").mkdir(parents=True, exist_ok=True)
        (ONEMEMORY_DIR / "amygdala").mkdir(parents=True, exist_ok=True)
        print("[OneMemory] Addon loaded — intercepting ChatGPT conversations")

    def response(self, flow: http.HTTPFlow) -> None:
        """Called for every HTTP response flowing through the proxy."""
        # Only intercept ChatGPT conversation API
        if not flow.request.pretty_host in ("chatgpt.com", "chat.openai.com"):
            return
        if CHATGPT_CONVERSATION_PATH not in flow.request.path:
            return
        if flow.request.method != "POST":
            return

        try:
            self._capture(flow)
        except Exception as e:
            print(f"[OneMemory] Capture error: {e}")

    def _capture(self, flow: http.HTTPFlow) -> None:
        # Parse request body (user's message)
        request_body = json.loads(flow.request.get_text())
        user_message = self._extract_user_message(request_body)

        # Parse response body (assistant's reply) — it's streamed SSE
        response_text = flow.response.get_text()
        assistant_message, model = self._extract_assistant_response(response_text)

        if not user_message and not assistant_message:
            return

        # Build conversation record
        conv_id = datetime.now(timezone.utc).strftime("%H%M%S%f")[:12]
        conversation = {
            "id": conv_id,
            "provider": "openai",
            "model": model or request_body.get("model", "chatgpt"),
            "messages": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"source": "chatgpt-web"},
        }
        if user_message:
            conversation["messages"].append({"role": "user", "content": user_message})
        if assistant_message:
            conversation["messages"].append({"role": "assistant", "content": assistant_message})

        # Save to hippocampus
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_dir = HIPPOCAMPUS_DIR / today
        today_dir.mkdir(parents=True, exist_ok=True)
        filepath = today_dir / f"{conv_id}.json"
        filepath.write_text(json.dumps(conversation, indent=2))

        # Update index
        index_path = HIPPOCAMPUS_DIR / "index.json"
        index = {"conversations": {}}
        if index_path.exists():
            index = json.loads(index_path.read_text())
        index["conversations"][conv_id] = str(filepath)
        index_path.write_text(json.dumps(index, indent=2))

        preview = user_message[:60] if user_message else "(no user msg)"
        print(f"[OneMemory] Captured: {preview}...")

    def _extract_user_message(self, request_body: dict) -> str:
        """Extract user message from ChatGPT's request payload."""
        messages = request_body.get("messages", [])
        for msg in reversed(messages):
            if msg.get("author", {}).get("role") == "user":
                parts = msg.get("content", {}).get("parts", [])
                text_parts = [p for p in parts if isinstance(p, str)]
                if text_parts:
                    return " ".join(text_parts)
        return ""

    def _extract_assistant_response(self, raw: str) -> tuple[str, str]:
        """Extract assistant's full reply from streamed SSE response."""
        assistant_content = ""
        model = ""

        for line in raw.split("\n"):
            line = line.strip()
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                continue

            # ChatGPT streams message objects with content.parts
            msg = chunk.get("message", {})
            if msg.get("author", {}).get("role") == "assistant":
                parts = msg.get("content", {}).get("parts", [])
                text_parts = [p for p in parts if isinstance(p, str)]
                if text_parts:
                    assistant_content = " ".join(text_parts)  # last chunk = full text
            if msg.get("metadata", {}).get("model_slug"):
                model = msg["metadata"]["model_slug"]

        return assistant_content, model


addons = [OneMemoryAddon()]
