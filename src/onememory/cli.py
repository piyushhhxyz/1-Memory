"""OneMemory CLI — one command to rule them all."""

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="onememory", help="OneMemory — your brain-inspired AI memory system"
)
console = Console()

ADDON_PATH = Path(__file__).parent / "interceptor" / "addon.py"


@app.command()
def init():
    """Initialize the ~/.onememory/ directory structure."""
    from onememory.config import Config

    config = Config()
    config.ensure_dirs()
    console.print(Panel(f"[green]OneMemory initialized at {config.base_dir}[/green]"))


@app.command()
def start(port: int = 8080):
    """Start the mitmproxy interceptor — captures ChatGPT conversations."""
    console.print(
        Panel(
            f"[bold green]OneMemory Interceptor starting on port {port}[/bold green]\n\n"
            f"[yellow]1.[/yellow] Set system proxy to [cyan]localhost:{port}[/cyan]\n"
            f"[yellow]2.[/yellow] Install CA cert (one time): open [cyan]http://mitm.it[/cyan]\n"
            f"[yellow]3.[/yellow] Chat on [cyan]chatgpt.com[/cyan] — conversations auto-captured",
            title="OneMemory",
        )
    )
    subprocess.run(["mitmdump", "-p", str(port), "-s", str(ADDON_PATH), "--quiet"])


@app.command()
def server(port: int = 11411):
    """Start the REST API server (optional, for dashboards/scripts)."""
    import uvicorn

    console.print(f"[green]OneMemory API server on port {port}[/green]")
    uvicorn.run("onememory.interceptor.proxy:app", host="0.0.0.0", port=port, log_level="info")


@app.command(name="mcp-serve")
def mcp_serve(
    http: bool = typer.Option(False, "--http", help="Run as HTTP/SSE server (for claude.com)"),
    port: int = typer.Option(8765, "--port", "-p", help="Port for HTTP/SSE mode"),
):
    """Start the MCP server (for Claude Code / Cursor / claude.com)."""
    from onememory.mcp_server.server import main

    if http:
        console.print(
            Panel(
                f"[bold green]OneMemory MCP server (SSE) on port {port}[/bold green]\n\n"
                f"[yellow]1.[/yellow] Run [cyan]ngrok http {port}[/cyan] in another terminal\n"
                f"[yellow]2.[/yellow] Copy the ngrok URL\n"
                f"[yellow]3.[/yellow] claude.com → Settings → Integrations → Add MCP → paste URL",
                title="OneMemory MCP (HTTP)",
            )
        )
        main(transport="sse", port=port)
    else:
        main(transport="stdio")


@app.command()
def status():
    """Show memory stats."""
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
        console.print(
            f"  [{r.entry.category}] {r.entry.content} [dim](score: {r.score:.2f})[/dim]"
        )


@app.command()
def remember(content: str, category: str = "general", tags: str = ""):
    """Store a new memory manually."""
    from onememory.brain import create_brain

    brain = create_brain()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    mid = brain.remember(content, category, tag_list)
    console.print(f"[green]Remembered:[/green] {content} [dim](id: {mid})[/dim]")


@app.command()
def dream():
    """Run sleep consolidation — extract memories from today's conversations."""
    from onememory.brain.amygdala import Amygdala
    from onememory.brain.cortex import Cortex
    from onememory.brain.hippocampus import Hippocampus
    from onememory.config import Config
    from onememory.consolidation.dreamer import Dreamer

    config = Config()
    config.ensure_dirs()
    dreamer = Dreamer(config, Hippocampus(config), Cortex(config), Amygdala(config))
    result = dreamer.dream()

    if result["status"] == "nothing_to_consolidate":
        console.print("[yellow]No conversations to consolidate.[/yellow]")
    else:
        console.print(
            Panel(
                f"[green]Consolidated {result['conversations']} conversations "
                f"into {result['memories_created']} memories[/green]",
                title="Dream Complete",
            )
        )


@app.command()
def recent(limit: int = 10):
    """Show recently captured conversations."""
    from onememory.brain import create_brain

    brain = create_brain()
    convos = brain.get_recent_conversations(limit)
    if not convos:
        console.print("[yellow]No conversations captured yet.[/yellow]")
        return
    for c in convos:
        user_msgs = [m for m in c.messages if m.role == "user"]
        assistant_msgs = [m for m in c.messages if m.role == "assistant"]
        user_text = user_msgs[0].content[:80] if user_msgs else "(no user message)"
        assistant_text = assistant_msgs[0].content[:80] if assistant_msgs else ""
        agent = c.metadata.get("agent", "unknown") if c.metadata else "unknown"
        console.print(f"  [cyan]\\[{agent}:{c.model}][/cyan] {user_text}")
        if assistant_text:
            console.print(f"    [dim]→ {assistant_text}[/dim]")


@app.command()
def clear(yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")):
    """Clear today's captured conversations."""
    from datetime import datetime, timezone

    from onememory.config import Config

    config = Config()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_file = config.hippocampus_dir / f"{today}.json"
    if not today_file.exists():
        console.print("[yellow]No conversations captured today.[/yellow]")
        return
    if not yes:
        typer.confirm(
            f"This will delete today's conversations ({today}). Continue?", abort=True
        )
    today_file.unlink()
    console.print(f"[green]Today's conversations cleared ({today}).[/green]")


if __name__ == "__main__":
    app()
