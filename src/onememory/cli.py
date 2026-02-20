import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(name="onememory", help="OneMemory — your brain-inspired AI memory system")
console = Console()

ADDON_PATH = Path(__file__).parent / "interceptor" / "addon.py"


@app.command()
def init():
    """Initialize OneMemory directory structure."""
    from onememory.config import Config
    config = Config()
    config.ensure_dirs()
    console.print(Panel(f"[green]OneMemory initialized at {config.base_dir}[/green]"))


@app.command()
def start(port: int = 8080):
    """Start the mitmproxy interceptor — captures ChatGPT traffic."""
    console.print(Panel(
        f"[bold green]OneMemory Interceptor starting on port {port}[/bold green]\n\n"
        f"[yellow]Step 1:[/yellow] Configure your browser/system proxy to [cyan]localhost:{port}[/cyan]\n"
        f"[yellow]Step 2:[/yellow] Install the mitmproxy CA cert (one time):\n"
        f"         Open [cyan]http://mitm.it[/cyan] in your browser after starting\n"
        f"[yellow]Step 3:[/yellow] Chat on [cyan]chatgpt.com[/cyan] — conversations auto-captured\n",
        title="OneMemory"
    ))
    # Run mitmdump with our addon
    subprocess.run(
        ["mitmdump", "-p", str(port), "-s", str(ADDON_PATH)],
    )


@app.command()
def server(port: int = 11411):
    """Start the OneMemory API server (for search, status, etc.)."""
    import uvicorn
    console.print(Panel(
        f"[bold green]OneMemory API server on port {port}[/bold green]\n"
        f"  Health: [cyan]http://localhost:{port}/health[/cyan]\n"
        f"  Memories: [cyan]http://localhost:{port}/api/memories[/cyan]",
        title="OneMemory"
    ))
    uvicorn.run("onememory.interceptor.proxy:app", host="0.0.0.0", port=port, log_level="info")


@app.command(name="mcp-serve")
def mcp_serve():
    """Start the MCP server (for Claude Code / Cursor)."""
    from onememory.mcp_server.server import main
    main()


@app.command()
def status():
    """Show OneMemory status."""
    from onememory.brain import create_brain
    brain = create_brain()
    s = brain.status()
    table = Table(title="OneMemory Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Memory Directory", s["memory_dir"])
    table.add_row("Conversations Captured", str(s["conversations_captured"]))
    table.add_row("Memories Stored", str(s["memories_stored"]))
    console.print(table)


@app.command()
def search(query: str, limit: int = 10):
    """Search your memories."""
    from onememory.brain import create_brain
    brain = create_brain()
    results = brain.search(query, limit)
    if not results:
        console.print("[yellow]No memories found.[/yellow]")
        return
    for r in results:
        console.print(f"  [{r.entry.category}] {r.entry.content} [dim](score: {r.score:.2f})[/dim]")


@app.command()
def remember(content: str, category: str = "general", tags: str = ""):
    """Store a new memory."""
    from onememory.brain import create_brain
    brain = create_brain()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    mid = brain.remember(content, category, tag_list)
    console.print(f"[green]Remembered:[/green] {content} [dim](id: {mid})[/dim]")


@app.command()
def dream():
    """Run sleep consolidation — extract memories from today's conversations."""
    from onememory.config import Config
    from onememory.brain.hippocampus import Hippocampus
    from onememory.brain.cortex import Cortex
    from onememory.brain.amygdala import Amygdala
    from onememory.consolidation.dreamer import Dreamer

    config = Config()
    config.ensure_dirs()
    dreamer = Dreamer(config, Hippocampus(config), Cortex(config), Amygdala(config))
    result = dreamer.dream()

    if result["status"] == "nothing_to_consolidate":
        console.print("[yellow]No conversations to consolidate.[/yellow]")
    else:
        console.print(Panel(
            f"[green]Consolidated {result['conversations']} conversations into {result['memories_created']} memories[/green]",
            title="Dream Complete"
        ))


@app.command()
def recent(limit: int = 10):
    """Show recent captured conversations."""
    from onememory.brain import create_brain
    brain = create_brain()
    convos = brain.get_recent_conversations(limit)
    if not convos:
        console.print("[yellow]No conversations captured yet.[/yellow]")
        return
    for c in convos:
        user_msgs = [m for m in c.messages if m.role == "user"]
        preview = user_msgs[0].content[:80] if user_msgs else "(no user message)"
        console.print(f"  [{c.provider}:{c.model}] {preview}")


if __name__ == "__main__":
    app()
