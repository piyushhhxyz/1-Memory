# OneMemory — Hackathon Pitch

## One-liner
**One memory for all your AIs.** A brain-inspired, fully local system that captures your ChatGPT conversations via a network proxy and makes them available to Claude (and any AI).

## The Problem (30 seconds)
Every AI has amnesia across platforms. You tell ChatGPT your name, your preferences, your project context. Open Claude — blank slate. Open Gemini — blank slate. You are the common thread, but no AI knows that.

## The Insight
Your brain doesn't store separate memories for each person you talk to. It has ONE memory system — hippocampus for fast capture, cortex for long-term storage, amygdala for importance, sleep for consolidation. We built that for AI.

## The Solution (OneMemory)
1. **Local MITM proxy** intercepts your ChatGPT conversations at the network level
2. **Brain-inspired storage** captures, scores, and organizes memories
3. **Dream consolidation** extracts structured facts from raw conversations
4. **MCP server** serves your memories to Claude Code

**Everything is local files.** No cloud, no database, no vendor lock-in. `~/.onememory/` — copy it to a USB drive, plug it in anywhere.

## Demo Script (5 minutes)

### Act 1 — "The Problem" (30s)
- Open ChatGPT, tell it about yourself
- Open Claude — blank slate, knows nothing
- "These platforms don't talk to each other"

### Act 2 — "OneMemory Captures" (90s)
- `onememory start` — proxy running, intercepting HTTPS
- Chat with ChatGPT: "My name is Piyush, I'm building OneMemory, I love Python"
- Show terminal: `[OneMemory] Captured: My name is Piyush...`
- `onememory status` → "1 conversation captured"

### Act 3 — "Dream Consolidation" (60s)
- Run `onememory dream`
- Show: "Consolidated 1 conversation into 2 memories"
- `onememory search "Piyush"` → shows identity + preferences
- `cat ~/.onememory/cortex/*.json` — just plain JSON files

### Act 4 — "Claude Knows You" (90s)
- Claude Code with MCP connected
- Ask: "What do you know about me?"
- Claude returns: identity, preferences, recent conversations
- Ask it to help with your project — it already knows your stack

### Act 5 — "It's Just Files" (30s)
- `ls ~/.onememory/cortex/`
- "Everything is JSON. No database. No cloud. Your brain, your data."

## Architecture Highlights
- **Brain-inspired**: Hippocampus → Amygdala → Cortex → Prefrontal Cortex
- **Design patterns**: Repository, Strategy, Observer, Facade, Factory, Protocol
- **Network-level interception**: mitmproxy captures real HTTPS traffic
- **Zero dependencies for storage**: Plain files, portable, git-trackable
- **Privacy-first**: Nothing leaves localhost

## What Makes This Different
- Not another ChatGPT wrapper
- Not another RAG system
- It's a **personal memory layer** — sits between you and ALL your AIs
- Neuroscience-inspired architecture (not just marketing, it's the actual code structure)
- Captures from the real ChatGPT web app, not a toy API demo
- Fully local, fully portable, fully yours
