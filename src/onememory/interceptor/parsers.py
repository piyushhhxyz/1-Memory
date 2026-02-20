from __future__ import annotations
import json
from typing import Protocol, runtime_checkable
from onememory.models import Conversation, Message, Provider


@runtime_checkable
class ConversationParser(Protocol):
    def can_parse(self, path: str) -> bool: ...
    def parse(self, request_body: dict, response_body: dict, model: str) -> Conversation: ...


class OpenAIParser:
    def can_parse(self, path: str) -> bool:
        return "chat/completions" in path

    def parse(self, request_body: dict, response_body: dict, model: str) -> Conversation:
        messages = []
        for m in request_body.get("messages", []):
            content = m.get("content", "")
            if isinstance(content, list):
                # multimodal: extract text parts
                content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            messages.append(Message(role=m.get("role", "user"), content=content))

        # Extract assistant response
        choices = response_body.get("choices", [])
        if choices:
            assistant_msg = choices[0].get("message", {})
            content = assistant_msg.get("content", "")
            if content:
                messages.append(Message(role="assistant", content=content))

        return Conversation(
            provider=Provider.OPENAI,
            model=model or request_body.get("model", "unknown"),
            messages=messages,
        )


class AnthropicParser:
    def can_parse(self, path: str) -> bool:
        return "messages" in path

    def parse(self, request_body: dict, response_body: dict, model: str) -> Conversation:
        messages = []
        # System message
        system = request_body.get("system", "")
        if system:
            if isinstance(system, list):
                system = " ".join(s.get("text", "") for s in system if isinstance(s, dict))
            messages.append(Message(role="system", content=system))

        for m in request_body.get("messages", []):
            content = m.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"
                )
            messages.append(Message(role=m.get("role", "user"), content=content))

        # Extract assistant response
        resp_content = response_body.get("content", [])
        if isinstance(resp_content, list):
            text_parts = [p.get("text", "") for p in resp_content if isinstance(p, dict) and p.get("type") == "text"]
            if text_parts:
                messages.append(Message(role="assistant", content=" ".join(text_parts)))

        return Conversation(
            provider=Provider.ANTHROPIC,
            model=model or request_body.get("model", "unknown"),
            messages=messages,
        )


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: list[ConversationParser] = [OpenAIParser(), AnthropicParser()]

    def get_parser(self, path: str) -> ConversationParser | None:
        for p in self._parsers:
            if p.can_parse(path):
                return p
        return None
