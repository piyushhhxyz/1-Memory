# OneMemory — Hackathon Pitch

## One-liner
**One memory for all your AIs.** Intercepts your ChatGPT conversations via a local proxy and makes them available to Claude via MCP.

## The Problem (30s)
Every AI has amnesia across platforms. Tell ChatGPT your name — Claude doesn't know it. Tell Gemini your preferences — Cursor has no idea. You are the common thread, but no AI knows that.

## The Insight
Your brain doesn't keep separate memories for each person you talk to. It has ONE memory system — hippocampus for fast capture, cortex for long-term storage, amygdala for importance, sleep for consolidation. We built that for AI.

## The Solution
1. **Local mitmproxy** intercepts ChatGPT web conversations at the network level
2. **Brain-inspired storage** captures, scores, and organizes memories
3. **Dream consolidation** extracts structured facts from raw conversations
4. **MCP server** serves your memories to Claude Code

Everything is local JSON files. No cloud. No database. `~/.onememory/` — copy it anywhere.

## Demo Script (5 min)

### Act 1 — "The Problem" (30s)
Open ChatGPT, tell it your name and preferences. Open Claude — blank slate.

### Act 2 — "OneMemory Captures" (90s)
- `onememory start` — interceptor running
- Chat on ChatGPT: "My name is Piyush, I love Python, I'm building OneMemory"
- Terminal shows: `[OneMemory] Captured (gpt-5-2): My name is Piyush...`
- `onememory status` → conversations captured

### Act 3 — "Dream Consolidation" (60s)
- `onememory dream` → "Consolidated 3 conversations into 5 memories"
- `onememory search "Piyush"` → shows identity + preferences

### Act 4 — "Claude Knows You" (90s)
- Claude Code with MCP connected
- "What do you know about me?" → identity, preferences, knowledge
- Ask for help with your project → it already knows your stack

### Act 5 — "It's Just Files" (30s)
`cat ~/.onememory/cortex/*.json` — plain JSON. Your brain, your data.

## What Makes This Different
- Captures from the **real ChatGPT web app** via network interception
- **Neuroscience-inspired** architecture — not a gimmick, it's the code structure
- **Fully local** — nothing leaves your machine
- **Portable** — plain files, copy anywhere
- Not a RAG system. Not a wrapper. A **personal memory layer** for all your AIs.
