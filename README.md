# OneMemory

**One memory for all your AIs.**

You tell ChatGPT your name, your preferences, what you're working on. Then you open Claude — blank slate. Switch to Gemini — blank slate. Every AI has amnesia. Your context, your identity, scattered across a dozen apps that will never talk to each other.

OneMemory fixes this. It intercepts your ChatGPT conversations at the network level, consolidates them into structured memories, and serves them to Claude via MCP. **Your brain, portable across every AI.**

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
| **Cortex** | Long-term semantic storage | Consolidated memories in `cortex/` |
| **Amygdala** | Emotional salience / importance | Importance scoring via keyword heuristics |
| **Prefrontal Cortex** | Executive retrieval & orchestration | Query facade that ties everything together |
| **Sleep consolidation** | Transfers hippocampus → cortex | `onememory dream` command |

This isn't just a cute metaphor — it's the actual code architecture. Fast capture, importance scoring, consolidation during "sleep", and orchestrated retrieval. Just like your brain.

### The Hippocampal-Cortical Memory System

The human memory system has a two-stage architecture (McClelland et al., 1995):

1. **Hippocampus** — fast, episodic recording of raw experiences
2. **Neocortex** — slow, semantic consolidation into structured knowledge

The transfer happens during **sleep** — your brain replays the day's experiences and extracts patterns. This is why "sleeping on it" helps you learn.

OneMemory mirrors this:
- `hippocampus/` = fast, raw conversation capture
- `cortex/` = consolidated, structured memories
- `onememory dream` = the "sleep" that transfers from one to the other

### The Amygdala: Not Everything Matters Equally

Your brain doesn't store every experience with equal weight. The amygdala tags experiences with emotional significance.

OneMemory's amygdala scores conversations by salience: mentions of identity ("my name is"), preferences ("I prefer"), strong opinions ("I love/hate") get higher scores. Low-salience chatter gets deprioritized during consolidation.

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
                    │ onememory dream
                    ▼
        ┌───────────────────────┐
        │   Amygdala → Cortex   │  scored + structured in ~/.onememory/cortex/
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │     MCP Server        │  Claude Code reads your memories
        └───────────────────────┘
```

### Step 1: Intercept

A local mitmproxy instance intercepts ChatGPT's `backend-anon/f/conversation` endpoint. Our addon parses the v1 delta-encoded SSE stream — collecting text append patches to reconstruct both the user's message and the assistant's full reply. Everything stays local.

### Step 2: Store & Score

Conversations land in `~/.onememory/hippocampus/` as raw JSON files, indexed for fast lookup. The Amygdala scores each conversation's importance based on personal information signals.

### Step 3: Consolidate

`onememory dream` runs sleep consolidation — it reads today's conversations, extracts structured facts (identity, preferences, knowledge), and stores them in the Cortex.

### Step 4: Recall

The MCP server exposes your memories to Claude Code. Ask Claude "what do you know about me?" — it returns your full context.

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

### Start Capturing

```bash
source .venv/bin/activate
networksetup -setwebproxy "Wi-Fi" localhost 8080
networksetup -setsecurewebproxy "Wi-Fi" localhost 8080
onememory start
```

Open chatgpt.com and chat. You'll see in the terminal:
```
[OneMemory] Captured (gpt-5-2): My name is Piyush and I love Python
[OneMemory] Reply: Nice to meet you Piyush!
[OneMemory] Saved: ~/.onememory/hippocampus/2026-02-21/073721.json
```

### Stop Capturing

```bash
networksetup -setwebproxystate "Wi-Fi" off
networksetup -setsecurewebproxystate "Wi-Fi" off
kill $(lsof -ti :8080)
```

### Daily Use

```bash
onememory recent              # see captured conversations
onememory dream               # consolidate into memories
onememory status              # memory stats
onememory search "python"     # search memories
```

### Connect Claude Code

```bash
claude mcp add onememory -- bash -c "cd $(pwd) && source .venv/bin/activate && onememory mcp-serve"
```

Ask Claude: **"What do you know about me?"**

### If It Breaks

```bash
kill $(lsof -ti :8080)       # kill stale process
onememory start               # restart fresh
```

---

## Troubleshooting

If the interceptor stops capturing conversations (or captures user messages but misses assistant replies), run through this checklist:

### 1. Is mitmdump running?

```bash
lsof -i :8080
```

If nothing shows up, start it:

```bash
onememory start
```

If something **other** than `mitmdump` is using port 8080, kill it first:

```bash
kill $(lsof -ti :8080)
onememory start
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

### 4. Stale process? Restart it

If mitmdump has been running for a long time and stops capturing properly, just restart it:

```bash
kill $(lsof -ti :8080)
onememory start
```

### 5. Debug mode

Run without `--quiet` to see all traffic and errors in real time:

```bash
mitmdump -p 8080 -s src/onememory/interceptor/addon.py
```

You should see `[OneMemory] Captured (...)` lines when you chat on ChatGPT.

---

## CLI Commands

| Command | What it does |
|---------|-------------|
| `onememory init` | Create `~/.onememory/` directory structure |
| `onememory start` | Start mitmproxy interceptor (captures ChatGPT) |
| `onememory status` | Show memory stats |
| `onememory recent` | Show recently captured conversations |
| `onememory search "query"` | Search your memories |
| `onememory remember "text" --category identity` | Manually store a memory |
| `onememory dream` | Consolidate conversations into structured memories |
| `onememory mcp-serve` | Start MCP server for Claude Code |
| `onememory server` | Start REST API server (optional) |

## MCP Tools (for Claude)

| Tool | What it does |
|------|-------------|
| `get_context` | Full user context — identity, preferences, knowledge |
| `search_memory` | Search for specific memories |
| `list_memories` | List all stored memories |
| `remember` | Store a new memory |
| `get_recent_conversations` | See recent captured conversations |

---

## Architecture

### Why a Local MITM Proxy?

We use mitmproxy — a battle-tested HTTPS proxy — with a custom addon. This:

- **Works with the real ChatGPT web app** — not a toy API demo
- **Captures actual network traffic** — request + response, structured data
- **Works with any browser** — not locked to Chrome
- **Extensible** — add Gemini, Perplexity, etc. by matching new endpoints

### Why Plain Files?

Everything is JSON in `~/.onememory/`. No SQLite, no Postgres, no vector stores.

- Copy the folder to a USB drive. Done.
- `cat` any file to see what's stored.
- Git-trackable. Portable. Yours.

```
~/.onememory/
├── hippocampus/           # Raw captured conversations
│   ├── index.json         # Conversation index
│   └── 2026-02-21/        # Today's conversations
├── cortex/                # Consolidated memories
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
| Storage | Plain JSON files |
| API server | FastAPI + uvicorn |
| MCP server | FastMCP |
| CLI | Typer + Rich |
| Data models | Pydantic v2 |

---

## The Vision

OneMemory is a proof of concept for a bigger idea: **you should own your AI context**.

Today, your preferences, your communication style, your project context — it's all locked inside platforms you don't control. OneMemory is a local-first, file-based, portable memory layer that sits between you and every AI you use.

### Future Directions

- **More AI platforms** — Gemini, Perplexity, Grok (add endpoint patterns to the addon)
- **LLM consolidation** — use a local LLM for smarter memory extraction
- **Embedding search** — local embeddings for semantic search
- **Memory decay** — older, less-accessed memories fade over time
- **Cross-device sync** — sync via git or Syncthing

---

**Zero databases. Zero vector stores. Zero cloud services. Just files on your disk.**

*Built to prove that your AI memory should belong to you.*
