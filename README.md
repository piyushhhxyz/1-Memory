# OneMemory 🧠

**One memory for all your AIs.**

You tell ChatGPT your name, your preferences, what you're working on. Then you open Claude — blank slate. Switch to Gemini — blank slate. Every AI has amnesia. Your context, your identity, scattered across a dozen apps that will never talk to each other.

OneMemory fixes this. It captures your conversations from any AI app, consolidates them into structured memories, and serves them to any AI that asks. **Your brain, portable across every AI.**

---

## The Problem

We did the research. Here's what we found:

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

### The Neuroscience Inspiration

We modeled OneMemory after how the human brain actually handles memory:

| Brain Region | Function | OneMemory Equivalent |
|-------------|----------|---------------------|
| **Hippocampus** | Fast capture of new experiences | Raw conversation capture |
| **Cortex** | Long-term semantic storage | Consolidated structured memories |
| **Amygdala** | Emotional salience / importance | Importance scoring |
| **Prefrontal Cortex** | Executive retrieval & orchestration | Query facade |
| **Sleep consolidation** | Transfers memories from hippocampus → cortex | `onememory dream` command |

This isn't just a cute metaphor — it's the actual architecture. Fast capture, importance scoring, consolidation during "sleep", and orchestrated retrieval. Just like your brain.

---

## How It Works

```
        You chatting on chatgpt.com
                    │
                    ▼
        ┌───────────────────────┐
        │   Local MITM Proxy    │  ← intercepts HTTPS traffic
        │   (mitmproxy:8080)    │
        └───────────┬───────────┘
                    │ captures conversations
                    ▼
┌─────────────────────────────────────────────────────────┐
│                    OneMemory Brain                        │
│                  (~/.onememory/)                          │
│                                                          │
│  ┌─────────────┐  ┌────────┐  ┌──────────┐             │
│  │ Hippocampus │→ │Amygdala│→ │  Cortex  │             │
│  │ (capture)   │  │(score) │  │ (store)  │             │
│  └─────────────┘  └────────┘  └──────────┘             │
│                        ↑                                 │
│               ┌────────────────┐                        │
│               │Prefrontal Cortex│ ← query orchestrator  │
│               └────────────────┘                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌───────────────────────┐
        │     MCP Server        │  ← Claude Code reads your memories
        │     (stdio)           │
        └───────────────────────┘
                     │
                     ▼
            Claude knows you.
```

### Step 1: Intercept (Local Proxy)

A local mitmproxy instance sits between your browser and the internet. When you chat on chatgpt.com, our addon script intercepts the API call to `backend-api/conversation`, reads both your message and ChatGPT's response, and saves it locally. **Zero data leaves your machine** — conversations are stored as plain JSON files.

### Step 2: Store & Score (Hippocampus + Amygdala)

Conversations land in `~/.onememory/hippocampus/` as raw JSON. The Amygdala scores each conversation's importance based on personal information signals ("my name is", "I prefer", "I always use", etc.). High-salience conversations are prioritized during consolidation.

### Step 3: Consolidate (Dream)

Run `onememory dream` to consolidate today's conversations. Like sleep consolidation in your brain, this extracts structured facts from raw conversations and stores them in the Cortex (long-term memory). Identity statements, preferences, knowledge — all categorized automatically.

### Step 4: Recall (MCP Server)

The MCP server exposes your memories to Claude Code (and any MCP-compatible AI). When you ask Claude "what do you know about me?", it searches your consolidated memories and returns your full context — identity, preferences, knowledge, recent conversations.

---

## Architecture: Why These Choices

### Local MITM Proxy (Not a Browser Extension)

We use mitmproxy — a battle-tested, open-source HTTPS proxy — with a custom addon script. This approach:

- **Works with any browser** — not locked to Chrome
- **Intercepts real network traffic** — no DOM hacking, no fragile selectors
- **Captures the actual API calls** — request + response, structured data
- **Extensible to any AI platform** — same proxy captures Gemini, Perplexity, etc.
- **One-time setup** — install CA cert once, then it just works

The addon script (`addon.py`) only looks at ChatGPT's conversation endpoint. All other traffic passes through untouched.

### Plain Files, Zero Databases

Everything is markdown and JSON in `~/.onememory/`. No SQLite, no Postgres, no vector stores.

**Why?**
- Copy the folder to a USB drive. Plug it into another machine. Done.
- `cat` any file to see what's stored. No proprietary formats.
- Git-trackable if you want version history of your memories.
- Zero dependencies for storage. No server to run, no migrations.

```
~/.onememory/
├── cortex/                    # Long-term memories (JSON)
│   ├── knowledge/             # Facts, skills, project info
│   ├── <id>.json              # Identity & preference memories
├── hippocampus/               # Raw captured conversations
│   ├── index.json             # Conversation index
│   └── 2026-02-21/            # Today's conversations
├── amygdala/
│   └── salience.json          # Importance scores
├── dreamlog/                  # Consolidation logs
└── working-memory/            # Current session context
```

### Token Overlap Search (No Embeddings)

We use simple token matching: tokenize the query, scan memories, score by `matching_terms / total_terms * importance`. It's O(n) over files.

**Why not embeddings?**
- Zero external dependencies (no OpenAI embeddings API, no local model)
- Works instantly on hundreds of memories (the realistic scale for personal use)
- Perfectly adequate for keyword-based personal memory recall
- Can be swapped for embedding search later without changing any interfaces

### Brain-Inspired Architecture (Not Just Marketing)

Every component maps to a real neuroscience concept, and every component uses a clean design pattern:

| Pattern | Where | Why |
|---------|-------|-----|
| **Repository** | `FileStore` | Abstract storage — swap to SQLite/S3 later |
| **Strategy** | Parsers | Different parsers per AI provider |
| **Observer** | `Hippocampus.on_capture()` | Notify Amygdala on new captures |
| **Facade** | `PrefrontalCortex` | Single entry point for all retrieval |
| **Factory** | `create_brain()` | Wire up dependencies cleanly |
| **Protocol** | All interfaces | Pythonic structural typing, no inheritance |

---

## Quick Start

### 1. Install OneMemory

```bash
cd onememory
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
onememory init
```

### 2. Install mitmproxy

```bash
brew install mitmproxy
```

### 3. Start the Interceptor

```bash
onememory start
```

### 4. Set Up Your Browser Proxy

Configure your browser (or system) to use HTTP proxy `localhost:8080`:
- **macOS**: System Preferences → Network → Advanced → Proxies → Web Proxy & Secure Web Proxy → `localhost:8080`
- **Or use a browser extension** like SwitchyOmega to route only chatgpt.com through the proxy

### 5. Install the CA Certificate (one time)

With the proxy running, open [http://mitm.it](http://mitm.it) in your browser and install the certificate for your OS.

### 6. Chat on ChatGPT

Go to [chatgpt.com](https://chatgpt.com) and have a conversation. Tell it about yourself. The proxy captures everything automatically. You'll see logs like:
```
[OneMemory] Captured: My name is Piyush and I love building AI tools...
```

### 7. Consolidate Memories

```bash
onememory dream
```

### 8. Connect Claude Code

```bash
claude mcp add onememory -- bash -c "cd $(pwd) && source .venv/bin/activate && onememory mcp-serve"
```

Now open Claude Code and ask: **"What do you know about me?"**

---

## CLI Commands

| Command | What it does |
|---------|-------------|
| `onememory init` | Create `~/.onememory/` directory structure |
| `onememory start` | Start the mitmproxy interceptor (captures ChatGPT) |
| `onememory server` | Start the API server (REST endpoints) |
| `onememory status` | Show memory stats |
| `onememory remember "text" --category identity` | Manually store a memory |
| `onememory search "query"` | Search your memories |
| `onememory dream` | Consolidate conversations → structured memories |
| `onememory recent` | Show recently captured conversations |
| `onememory mcp-serve` | Start MCP server for Claude Code |

## MCP Tools (for Claude)

| Tool | What it does |
|------|-------------|
| `search_memory` | Search for specific memories |
| `get_context` | Get full user context (identity, preferences, knowledge) |
| `list_memories` | List all stored memories |
| `remember` | Store a new memory |
| `get_recent_conversations` | See recent captured conversations |

---

## The Research Behind OneMemory

### Why Memory Matters More Than Intelligence

GPT-4, Claude, Gemini — they're all incredibly smart. But intelligence without memory is like a brilliant doctor who forgets every patient after each visit. The bottleneck isn't capability, it's continuity.

Research in cognitive science shows that human expertise comes not from raw processing power, but from **accumulated experience organized into retrievable patterns**. Chess grandmasters don't calculate better than computers — they recognize board patterns from thousands of games stored in memory. (Chase & Simon, 1973)

AI assistants today have raw processing power but zero accumulated experience with you. Every session starts cold.

### The Hippocampal-Cortical Memory System

The human memory system has a two-stage architecture (McClelland et al., 1995):

1. **Hippocampus** — fast, episodic recording of new experiences (like a TiVo)
2. **Neocortex** — slow, semantic consolidation into structured knowledge (like a Wikipedia)

The transfer from hippocampus to cortex happens during **sleep** — your brain literally replays the day's experiences and extracts patterns. This is why "sleeping on it" helps you learn.

OneMemory mirrors this exactly:
- `hippocampus/` = fast, raw conversation capture
- `cortex/` = consolidated, structured memories
- `onememory dream` = the "sleep" that transfers from one to the other

### The Amygdala: Not Everything Matters Equally

Your brain doesn't store every experience with equal weight. The amygdala tags experiences with emotional significance — that's why you remember your first kiss but not your 500th commute.

OneMemory's amygdala scores conversations by salience: mentions of identity ("my name is"), preferences ("I prefer"), strong opinions ("I love/hate") get higher scores. Low-salience chatter gets lower priority during consolidation.

### Why Local-First?

The move toward local-first AI memory is inevitable:
- **Privacy**: Your AI conversations contain some of the most intimate data about your thinking
- **Portability**: You switch tools, switch devices, switch providers — your memory should follow you
- **Ownership**: If a service shuts down, your data shouldn't disappear with it
- **Transparency**: You should be able to `cat` any memory file and see exactly what's stored

---

## The Vision

OneMemory is a proof of concept for a bigger idea: **you should own your AI context**.

Today, your preferences, your communication style, your project context — it's all locked inside platforms you don't control. If OpenAI shuts down your account tomorrow, your ChatGPT memories are gone. If you switch from Claude to Gemini, you start from zero.

OneMemory is a local-first, file-based, portable memory layer that sits between you and every AI you use. It's the beginning of a personal AI memory standard — not controlled by any company, stored on your machine, in formats you can read with `cat`.

### Future Directions

- **More AI platforms**: Gemini, Perplexity, Grok — add more patterns to the proxy addon
- **Embedding search**: Local embeddings for semantic search (no API calls)
- **LLM consolidation**: Use a local LLM (Llama, Qwen) for smarter memory extraction
- **Memory decay**: Older, less-accessed memories fade (like real memory)
- **Cross-device sync**: Sync via git, Syncthing, or any file sync tool
- **Web dashboard**: Visualize and manage your memories

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Interceptor | mitmproxy + custom addon | Battle-tested HTTPS proxy, any browser |
| Memory storage | Plain JSON files | Portable, readable, zero dependencies |
| API server | FastAPI + uvicorn | Async, fast, Python-native |
| MCP server | FastMCP | Native Claude Code integration |
| CLI | Typer + Rich | Beautiful terminal interface |
| Data models | Pydantic v2 | Validation, serialization, type safety |

**Zero databases. Zero vector stores. Zero cloud services. Just files on your disk.**

---

*Built for the hackathon. Built to prove that your AI memory should belong to you.*
