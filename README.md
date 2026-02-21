# OneMemory

**One memory for all your AIs.**

You tell ChatGPT your name, your preferences, what you're working on. Then you open Claude — blank slate. Switch to Gemini — blank slate. Every AI has amnesia. Your context, your identity, scattered across a dozen apps that will never talk to each other.

OneMemory fixes this. It intercepts your ChatGPT conversations at the network level, **automatically** consolidates them into structured memories, and serves them to Claude via MCP. **Your brain, portable across every AI.**

---

## The Problem

### Every AI Platform is a Walled Garden

| Platform | Memory | Portable? | Cross-platform? |
|----------|--------|-----------|-----------------|
| ChatGPT | Yes (limited) | No | No |
| Claude | Projects only | No | No |
| Gemini | Basic | No | No |
| Cursor | .cursorrules | Sort of | No |

Each platform wants to own your context. None of them share. **You** are the common thread across all these tools, but none of them know that.

### Why This Matters

Memory isn't a feature — it's the foundation of a real relationship with AI.

Without shared memory:
- You repeat yourself constantly ("I use Python", "I prefer functional style", "My project uses FastAPI")
- No AI builds a real model of who you are
- Your preferences and context are locked inside corporate silos
- Switching AI tools means starting from scratch

---

## The Neuroscience Behind OneMemory

We modeled OneMemory after how the human brain actually handles memory:

| Brain Region | Function | OneMemory Equivalent |
|-------------|----------|---------------------|
| **Hippocampus** | Fast capture of new experiences | Raw conversation capture in `hippocampus/` |
| **Cortex** | Long-term semantic storage | Consolidated memories in `cortex/` (vector search via ChromaDB) |
| **Amygdala** | Emotional salience / importance | Importance scoring via keyword heuristics |
| **Prefrontal Cortex** | Executive retrieval & orchestration | Query facade that ties everything together |
| **Auto-consolidation** | Real-time hippocampus → cortex transfer | Happens instantly on capture — no manual step needed |

This isn't just a cute metaphor — it's the actual code architecture. Fast capture, importance scoring, instant consolidation, and orchestrated retrieval. Just like your brain.

---

## How It Works

```
        You chatting on chatgpt.com
                    │
                    ▼
        ┌───────────────────────┐
        │   Local MITM Proxy    │  intercepts HTTPS via mitmproxy
        │   (localhost:8080)    │
        └───────────┬───────────┘
                    │ captures user + assistant messages
                    ▼
        ┌───────────────────────┐
        │     Hippocampus       │  raw JSON in ~/.onememory/hippocampus/
        └───────────┬───────────┘
                    │ auto-consolidation (instant, no manual step)
                    ▼
        ┌───────────────────────┐
        │   Amygdala → Cortex   │  scored + vectorized in ~/.onememory/cortex/
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │     MCP Server        │  Claude reads your memories via recall()
        └───────────────────────┘
```

### Step 1: Intercept

A local mitmproxy instance intercepts ChatGPT's `backend-anon/f/conversation` endpoint. Our addon parses the v1 delta-encoded SSE stream — collecting text append patches to reconstruct both the user's message and the assistant's full reply. Everything stays local.

### Step 2: Store, Score & Consolidate (automatic)

Conversations land in `~/.onememory/hippocampus/` as raw JSON files. **Immediately** after capture, the addon extracts facts (identity, preferences, knowledge) and stores them in the Cortex with deterministic content-based IDs — same content always gets the same ID, so duplicates are impossible.

### Step 3: Recall

The MCP server exposes a single `recall()` tool to Claude. It returns your full context — identity, preferences, knowledge, recent activity. Add a query to get semantic search results.

---

## Quick Start

### Setup (one time)

```bash
cd onememory
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
brew install mitmproxy
onememory init
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem
```

### Start Everything (one command)

```bash
# Terminal 1: Start proxy + MCP server
source .venv/bin/activate
networksetup -setwebproxy "Wi-Fi" localhost 8080
networksetup -setsecurewebproxy "Wi-Fi" localhost 8080
onememory up

# Terminal 2: Expose MCP to claude.com
ngrok http 8765
```

That's it. Chat on chatgpt.com — memories appear instantly. No `dream` step needed.

### Stop

```bash
# Ctrl+C in Terminal 1 (stops both proxy and MCP server)
networksetup -setwebproxystate "Wi-Fi" off
networksetup -setsecurewebproxystate "Wi-Fi" off
```

### Connect Claude Code

```bash
claude mcp add onememory -- bash -c "cd $(pwd) && source .venv/bin/activate && onememory mcp-serve"
```

Ask Claude: **"What do you know about me?"**

### Connect claude.com

1. Copy the ngrok URL from Terminal 2
2. claude.com → Settings → Integrations → Add MCP → paste the URL

---

## CLI Commands

### Run

| Command | What it does |
|---------|-------------|
| `onememory up` | **Start everything** — proxy interceptor + MCP server |
| `onememory init` | Create `~/.onememory/` directory structure |
| `onememory start` | Start mitmproxy interceptor only |
| `onememory mcp-serve` | Start MCP server only (stdio for Claude Code) |
| `onememory mcp-serve --http` | Start MCP server only (SSE for claude.com) |

### Inspect

| Command | What it does |
|---------|-------------|
| `onememory memories` | List all stored memories in a table |
| `onememory memories identity` | Filter by category (`identity`, `preference`, `knowledge`) |
| `onememory context` | Show exactly what Claude sees when it calls `recall()` |
| `onememory search "query"` | Semantic search across your memories |
| `onememory recent` | Show recently captured conversations |
| `onememory status` | Show memory stats (counts) |

### Manage

| Command | What it does |
|---------|-------------|
| `onememory remember "text"` | Manually store a memory |
| `onememory clear` | Clear today's captured conversations |
| `onememory reset --memories` | Clear all memories (cortex) only, keep conversations |
| `onememory reset` | **Nuke everything** — conversations + memories + scores |
| `onememory reset --yes` | Skip confirmation |
| `onememory dream` | *(deprecated)* One-time migration of old conversations |

## MCP Tools (for Claude)

Claude is instructed to **always call `recall()` first** at the start of every conversation to load your full context, and address you by name.

| Tool | What it does |
|------|-------------|
| `recall()` | Full user context — identity, preferences, knowledge, recent activity, stats |
| `recall(query="...")` | Full context + semantic search results matching the query |
| `remember(content, category)` | Store a new memory about the user |

---

## Troubleshooting

If the interceptor stops capturing conversations, run through this checklist:

### 1. Is everything running?

```bash
lsof -i :8080   # proxy
lsof -i :8765   # MCP server
```

If not, restart:

```bash
onememory up
```

### 2. Is the system proxy ON?

```bash
networksetup -getwebproxy "Wi-Fi"
networksetup -getsecurewebproxy "Wi-Fi"
```

Both should show `Enabled: Yes`, `Server: localhost`, `Port: 8080`. If not:

```bash
networksetup -setwebproxy "Wi-Fi" localhost 8080
networksetup -setsecurewebproxy "Wi-Fi" localhost 8080
```

### 3. Is the mitmproxy CA certificate trusted?

```bash
security verify-cert -c ~/.mitmproxy/mitmproxy-ca-cert.pem -p ssl
```

Should say `certificate verification successful`. If not:

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem
```

### 4. Debug mode

Run without `--quiet` to see all traffic and errors in real time:

```bash
mitmdump -p 8080 -s src/onememory/interceptor/addon.py
```

You should see `[OneMemory] Captured (...)` and `[OneMemory] Auto-stored: [...]` lines when you chat on ChatGPT.

---

## Architecture

### Why a Local MITM Proxy?

We use mitmproxy — a battle-tested HTTPS proxy — with a custom addon. This:

- **Works with the real ChatGPT web app** — not a toy API demo
- **Captures actual network traffic** — request + response, structured data
- **Works with any browser** — not locked to Chrome
- **Extensible** — add Gemini, Perplexity, etc. by matching new endpoints

### No Duplicates, Ever

Memories use **content-based deterministic IDs** (`md5(content)[:12]`). Same message = same ID = ChromaDB upsert overwrites instead of duplicating. Run consolidation 100 times — still no duplicates.

### Storage

```
~/.onememory/
├── hippocampus/           # Raw captured conversations
│   ├── 2026-02-21.json    # One file per day (all conversations)
│   └── 2026-02-20.json
├── cortex/                # Consolidated memories
│   ├── vectordb/          # ChromaDB vector store (semantic search)
│   └── knowledge/         # Facts and knowledge
├── amygdala/
│   └── salience.json      # Importance scores
├── dreamlog/              # Consolidation logs
└── working-memory/        # Session context
```

### Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Repository** | `FileStore` | Abstract storage — swap to SQLite/S3 later |
| **Observer** | `Hippocampus.on_capture()` | Notify Amygdala on new captures |
| **Facade** | `PrefrontalCortex` | Single entry point for all retrieval |
| **Factory** | `create_brain()` | Wire up dependencies cleanly |

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Interceptor | mitmproxy + custom addon |
| Storage | Plain JSON + ChromaDB vectors |
| MCP server | FastMCP (stdio + SSE) |
| CLI | Typer + Rich |
| Data models | Pydantic v2 |

---

## The Vision

OneMemory is a proof of concept for a bigger idea: **you should own your AI context**.

Today, your preferences, your communication style, your project context — it's all locked inside platforms you don't control. OneMemory is a local-first, portable memory layer that sits between you and every AI you use.

### Future Directions

- **More AI platforms** — Gemini, Perplexity, Grok (add endpoint patterns to the addon)
- **LLM consolidation** — use a local LLM for smarter memory extraction
- **Memory decay** — older, less-accessed memories fade over time
- **Cross-device sync** — sync via git or Syncthing

---

**One command. Instant memories. No duplicates. Your brain, your data.**

*Built to prove that your AI memory should belong to you.*
