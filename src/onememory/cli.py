"""OneMemory CLI — one command to rule them all."""

import os
import signal
import subprocess
import sys
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
def up(
    proxy_port: int = typer.Option(8080, "--proxy-port", help="Port for mitmproxy interceptor"),
    mcp_port: int = typer.Option(8765, "--mcp-port", help="Port for MCP SSE server"),
):
    """Start everything — proxy interceptor + MCP server. One command."""
    console.print(
        Panel(
            f"[bold green]OneMemory starting...[/bold green]\n\n"
            f"[yellow]1.[/yellow] Proxy interceptor on [cyan]localhost:{proxy_port}[/cyan]\n"
            f"[yellow]2.[/yellow] MCP server (SSE) on [cyan]localhost:{mcp_port}[/cyan]\n\n"
            f"[dim]In another terminal run:[/dim] [cyan]ngrok http {mcp_port}[/cyan]\n"
            f"[dim]Then add the ngrok URL to claude.com → Settings → Integrations[/dim]",
            title="OneMemory",
        )
    )

    # Start mitmdump as background subprocess
    mitm_proc = subprocess.Popen(
        ["mitmdump", "-p", str(proxy_port), "-s", str(ADDON_PATH), "--quiet"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    console.print(f"[green]Proxy interceptor started (PID {mitm_proc.pid})[/green]")

    # Handle Ctrl+C — kill both processes
    def _shutdown(signum, frame):
        console.print("\n[yellow]Shutting down...[/yellow]")
        mitm_proc.terminate()
        try:
            mitm_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            mitm_proc.kill()
        console.print("[green]OneMemory stopped.[/green]")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Run MCP server in foreground (blocks)
    try:
        from onememory.mcp_server.server import main as mcp_main
        mcp_main(transport="sse", port=mcp_port)
    finally:
        mitm_proc.terminate()
        mitm_proc.wait(timeout=5)


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
def memories(category: str = typer.Argument("", help="Filter by category: identity, preference, knowledge")):
    """List all stored memories — see what's in your cortex."""
    from onememory.brain import create_brain

    brain = create_brain()
    all_memories = brain.get_all_memories()
    if category:
        all_memories = [m for m in all_memories if m.category == category]
    if not all_memories:
        console.print("[yellow]No memories found.[/yellow]")
        return

    table = Table(title=f"Memories{f' ({category})' if category else ''}")
    table.add_column("Category", style="cyan", width=12)
    table.add_column("Content", style="white")
    table.add_column("Source", style="dim", width=20)
    table.add_column("ID", style="dim", width=14)
    for m in all_memories:
        table.add_row(m.category, m.content, m.source, m.id)
    console.print(table)
    console.print(f"\n[dim]Total: {len(all_memories)} memories[/dim]")


@app.command()
def context():
    """Show your full context — what Claude sees when it calls recall()."""
    from onememory.brain import create_brain

    brain = create_brain()
    ctx = brain.get_context()

    if ctx["identity"]:
        console.print("\n[bold cyan]Identity[/bold cyan]")
        for i in ctx["identity"]:
            console.print(f"  - {i}")
    if ctx["preferences"]:
        console.print("\n[bold cyan]Preferences[/bold cyan]")
        for p in ctx["preferences"]:
            console.print(f"  - {p}")
    if ctx["knowledge"]:
        console.print("\n[bold cyan]Knowledge[/bold cyan]")
        for k in ctx["knowledge"]:
            console.print(f"  - {k}")

    console.print(
        f"\n[dim]{ctx['total_memories']} memories, "
        f"{ctx['total_conversations']} conversations, "
        f"{ctx['recent_conversations']} recent[/dim]"
    )


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
    """[Deprecated] Consolidation now happens automatically. Run for a one-time migration."""
    console.print(
        "[yellow]Note: 'dream' is deprecated — consolidation now happens automatically when conversations are captured.[/yellow]\n"
        "[dim]Running one final consolidation for any un-processed conversations...[/dim]"
    )
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


@app.command()
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    memories_only: bool = typer.Option(False, "--memories", help="Only clear memories (cortex), keep conversations"),
):
    """Clear all memories and/or conversations. Start fresh."""
    import shutil
    from onememory.config import Config

    config = Config()

    if not yes:
        what = "all memories (cortex)" if memories_only else "ALL data (conversations + memories + scores)"
        typer.confirm(f"This will delete {what}. Are you sure?", abort=True)

    if memories_only:
        vectordb = config.cortex_dir / "vectordb"
        if vectordb.exists():
            shutil.rmtree(vectordb)
        console.print("[green]Memories cleared (cortex reset). Conversations kept.[/green]")
    else:
        for d in [config.hippocampus_dir, config.cortex_dir, config.amygdala_dir, config.dreamlog_dir]:
            if d.exists():
                shutil.rmtree(d)
        config.ensure_dirs()
        console.print("[green]Everything cleared. Fresh start.[/green]")


if __name__ == "__main__":
    app()
