# OneMemory — Hackathon Pitch

## One-liner
**One memory for all your AIs.** Intercepts your ChatGPT conversations via a local proxy, auto-consolidates them into structured memories, and serves them to Claude via MCP — one command, zero manual steps.

## The Problem (30s)
Every AI has amnesia across platforms. Tell ChatGPT your name — Claude doesn't know it. Tell Gemini your preferences — Cursor has no idea. You are the common thread, but no AI knows that.

## The Insight
Your brain doesn't keep separate memories for each person you talk to. It has ONE memory system — hippocampus for fast capture, cortex for long-term storage, amygdala for importance. We built that for AI.

## The Solution
1. **Local mitmproxy** intercepts ChatGPT web conversations at the network level
2. **Auto-consolidation** — memories are extracted and stored the instant you chat (no manual step)
3. **Deterministic deduplication** — same content = same ID = no duplicates, ever
4. **One MCP tool** — `recall()` gives Claude your full identity, preferences, knowledge, and recent activity

Everything is local. `~/.onememory/` — copy it anywhere.

## Demo Script (5 min)

### Act 1 — "The Problem" (30s)
Open ChatGPT, tell it your name and preferences. Open Claude — blank slate.

### Act 2 — "One Command" (60s)
- `onememory up` — starts proxy + MCP server in one command
- `ngrok http 8765` — expose to claude.com
- That's the entire setup. Two terminals.

### Act 3 — "Instant Memory" (90s)
- Chat on ChatGPT: "My name is Piyush, I love Python, I'm building OneMemory"
- Terminal shows:
  ```
  [OneMemory] Captured (gpt-5-2): My name is Piyush...
  [OneMemory] Auto-stored: [identity] My name is Piyush...
  ```
- `onememory memories` → table of all memories, already there. No `dream` step. Instant.
- `onememory context` → see exactly what Claude will see when it calls `recall()`

### Act 4 — "Claude Knows You" (90s)
- Claude calls `recall()` → gets identity, preferences, knowledge, recent activity
- "What do you know about me?" → full context, instantly
- Ask for help with your project → it already knows your stack

### Act 5 — "No Duplicates" (30s)
- Chat the same thing again on ChatGPT
- `onememory search "Piyush"` → still just one memory. Content-based IDs = automatic dedup.

### Act 6 — "Full CLI" (30s)
```
onememory memories            # see all memories
onememory context             # what Claude sees
onememory recent              # captured conversations
onememory reset --yes         # nuke everything, start fresh
```
Your brain, your data, full control.

## What Makes This Different
- **One command** to start everything (`onememory up`)
- **Instant consolidation** — no manual "dream" step, memories appear as you chat
- **Zero duplicates** — deterministic content-based IDs, run it 100 times, same result
- **One MCP tool** — `recall()` returns everything Claude needs in one call
- Captures from the **real ChatGPT web app** via network interception
- **Neuroscience-inspired** architecture — not a gimmick, it's the code structure
- **Fully local** — nothing leaves your machine
