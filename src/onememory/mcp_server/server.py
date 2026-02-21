"""MCP Server — exposes OneMemory to Claude Code and other MCP clients."""
from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from onememory.brain import create_brain

mcp = FastMCP(
    "OneMemory",
    instructions="Access the user's personal memory. Use these tools to recall what you know about the user.",
)
brain = create_brain()


@mcp.tool()
def search_memory(query: str, limit: int = 5) -> str:
    """Search the user's memory for relevant information."""
    results = brain.search(query, limit)
    if not results:
        return "No memories found matching that query."
    lines = []
    for r in results:
        lines.append(f"- [{r.entry.category}] {r.entry.content} (relevance: {r.score:.2f})")
    return "\n".join(lines)


@mcp.tool()
def get_context() -> str:
    """Get full context about the user — identity, preferences, knowledge. Call this at the start of conversations."""
    ctx = brain.get_context()
    parts = []
    if ctx["identity"]:
        parts.append("## Identity\n" + "\n".join(f"- {i}" for i in ctx["identity"]))
    if ctx["preferences"]:
        parts.append("## Preferences\n" + "\n".join(f"- {p}" for p in ctx["preferences"]))
    if ctx["knowledge"]:
        parts.append("## Knowledge\n" + "\n".join(f"- {k}" for k in ctx["knowledge"]))
    parts.append(f"\n**Stats:** {ctx['total_memories']} memories, {ctx['total_conversations']} conversations captured")
    return "\n\n".join(parts) if parts else "No memories stored yet."


@mcp.tool()
def list_memories(category: str = "") -> str:
    """List all stored memories, optionally filtered by category (identity, preference, knowledge)."""
    memories = brain.get_all_memories()
    if category:
        memories = [m for m in memories if m.category == category]
    if not memories:
        return "No memories found."
    return "\n".join(f"- **{m.category}**: {m.content}" for m in memories)


@mcp.tool()
def remember(content: str, category: str = "general", tags: str = "") -> str:
    """Store a new memory. Categories: identity, preference, knowledge, general."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    memory_id = brain.remember(content, category, tag_list)
    return f"Stored memory {memory_id}: {content}"


@mcp.tool()
def get_recent_conversations(limit: int = 5) -> str:
    """Get recent conversations captured from ChatGPT."""
    convos = brain.get_recent_conversations(limit)
    if not convos:
        return "No conversations captured yet."
    lines = []
    for c in convos:
        user_msgs = [m for m in c.messages if m.role == "user"]
        assistant_msgs = [m for m in c.messages if m.role == "assistant"]
        user_preview = user_msgs[0].content[:100] if user_msgs else ""
        assistant_preview = assistant_msgs[0].content[:100] if assistant_msgs else ""
        lines.append(f"- [{c.provider}:{c.model}] User: {user_preview}")
        if assistant_preview:
            lines.append(f"  Assistant: {assistant_preview}")
    return "\n".join(lines)


def main(transport: str = "stdio", port: int = 8765):
    if transport == "sse":
        from mcp.server.transport_security import TransportSecuritySettings
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = port
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        )
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
