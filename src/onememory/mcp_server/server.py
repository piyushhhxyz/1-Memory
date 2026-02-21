"""MCP Server — exposes OneMemory to Claude Code and other MCP clients."""
from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from onememory.brain import create_brain

mcp = FastMCP(
    "OneMemory",
    instructions=(
        "IMPORTANT: You MUST call recall() at the very start of EVERY conversation before responding to the user. "
        "This loads the user's identity, preferences, knowledge, and recent activity. "
        "Always address the user by their name if available. "
        "When the user shares new personal information, use remember() to store it."
    ),
)
brain = create_brain()


@mcp.tool()
def recall(query: str = "") -> str:
    """Recall everything you know about the user.
    No query → returns full context (identity, preferences, knowledge, recent activity, stats).
    With query → adds semantic search results matching the query."""
    parts = []

    # Always include full context
    ctx = brain.get_context()
    if ctx["identity"]:
        parts.append("## Identity\n" + "\n".join(f"- {i}" for i in ctx["identity"]))
    if ctx["preferences"]:
        parts.append("## Preferences\n" + "\n".join(f"- {p}" for p in ctx["preferences"]))
    if ctx["knowledge"]:
        parts.append("## Knowledge\n" + "\n".join(f"- {k}" for k in ctx["knowledge"]))

    # Recent activity
    recent = brain.get_recent_conversations(5)
    if recent:
        lines = []
        for c in recent:
            user_msgs = [m for m in c.messages if m.role == "user"]
            if user_msgs:
                lines.append(f"- [{c.provider}:{c.model}] {user_msgs[0].content[:100]}")
        if lines:
            parts.append("## Recent Activity\n" + "\n".join(lines))

    parts.append(f"\n**Stats:** {ctx['total_memories']} memories, {ctx['total_conversations']} conversations captured")

    # If query provided, add semantic search results
    if query:
        results = brain.search(query, 10)
        if results:
            search_lines = []
            for r in results:
                search_lines.append(f"- [{r.entry.category}] {r.entry.content} (relevance: {r.score:.2f})")
            parts.append("## Search Results for: " + query + "\n" + "\n".join(search_lines))
        else:
            parts.append(f"\n_No specific results found for '{query}'_")

    return "\n\n".join(parts) if parts else "No memories stored yet."


@mcp.tool()
def remember(content: str, category: str = "general", tags: str = "") -> str:
    """Store a new memory about the user. Categories: identity, preference, knowledge, general."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    memory_id = brain.remember(content, category, tag_list)
    return f"Stored memory {memory_id}: {content}"


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
