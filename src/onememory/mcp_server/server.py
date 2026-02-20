from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from onememory.brain import create_brain

mcp = FastMCP("OneMemory", instructions="Access the user's personal memory system. Use these tools to recall information about the user, their preferences, past conversations, and stored knowledge.")

brain = create_brain()


@mcp.tool()
def search_memory(query: str, limit: int = 5) -> str:
    """Search the user's memory for relevant information. Use this when you need to recall something about the user or find stored knowledge."""
    results = brain.search(query, limit)
    if not results:
        return "No memories found matching that query."
    lines = []
    for r in results:
        lines.append(f"- [{r.entry.category}] {r.entry.content} (relevance: {r.score:.2f})")
    return "\n".join(lines)


@mcp.tool()
def get_context() -> str:
    """Get full context about the user — identity, preferences, knowledge, and recent activity. Call this at the start of a conversation to understand who you're talking to."""
    ctx = brain.get_context()
    parts = []
    if ctx["identity"]:
        parts.append("## Identity\n" + "\n".join(f"- {i}" for i in ctx["identity"]))
    if ctx["preferences"]:
        parts.append("## Preferences\n" + "\n".join(f"- {p}" for p in ctx["preferences"]))
    if ctx["knowledge"]:
        parts.append("## Knowledge\n" + "\n".join(f"- {k}" for k in ctx["knowledge"]))
    parts.append(f"\n**Stats:** {ctx['total_memories']} memories, {ctx['total_conversations']} conversations captured")
    return "\n\n".join(parts) if parts else "No memories stored yet. The user is new."


@mcp.tool()
def list_memories(category: str = "") -> str:
    """List all stored memories, optionally filtered by category (identity, preference, general, knowledge)."""
    memories = brain.get_all_memories()
    if category:
        memories = [m for m in memories if m.category == category]
    if not memories:
        return "No memories found."
    lines = []
    for m in memories:
        tags = f" [{', '.join(m.tags)}]" if m.tags else ""
        lines.append(f"- **{m.category}**: {m.content}{tags}")
    return "\n".join(lines)


@mcp.tool()
def remember(content: str, category: str = "general", tags: str = "") -> str:
    """Store a new memory about the user. Categories: identity, preference, knowledge, general. Tags are comma-separated."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    memory_id = brain.remember(content, category, tag_list)
    return f"Stored memory {memory_id}: {content}"


@mcp.tool()
def get_recent_conversations(limit: int = 5) -> str:
    """Get recent conversations captured from AI apps the user has interacted with."""
    convos = brain.get_recent_conversations(limit)
    if not convos:
        return "No conversations captured yet."
    lines = []
    for c in convos:
        msg_preview = ""
        user_msgs = [m for m in c.messages if m.role == "user"]
        if user_msgs:
            msg_preview = user_msgs[0].content[:100]
        lines.append(f"- [{c.provider}:{c.model}] {msg_preview}...")
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
