# Contributing to OneMemory

Thanks for your interest in contributing to OneMemory! This guide will help you get started.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/piyushhhxyz/1-Memory.git
   cd 1-Memory
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Run the CLI**

   ```bash
   uv run onememory --help
   ```

## Project Structure

```
src/onememory/
├── brain/              # Core memory modules (hippocampus, cortex, amygdala, prefrontal)
├── consolidation/      # Memory consolidation (dreamer)
├── interceptor/        # Network proxy for capturing conversations
├── mcp_server/         # MCP server for Claude integration
├── cli.py              # Typer CLI entrypoint
├── config.py           # Configuration
└── models.py           # Pydantic data models
```

## How to Contribute

### Reporting Bugs

- Open an issue with a clear title and description
- Include steps to reproduce the bug
- Mention your OS, Python version, and any relevant environment details

### Suggesting Features

- Open an issue describing the feature and why it would be useful
- If possible, outline a rough implementation approach

### Submitting Code

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test your changes locally
5. Commit with a clear message:
   ```bash
   git commit -m "Add: brief description of change"
   ```
6. Push and open a pull request against `main`

### Code Style

- Follow existing patterns in the codebase
- Use type hints for function signatures
- Keep functions focused and well-named
- Add docstrings to public functions and classes

## Architecture Notes

OneMemory is modeled after the human brain's memory system:

| Module | Brain Analog | Role |
|--------|-------------|------|
| `hippocampus` | Hippocampus | Fast capture of raw conversations |
| `cortex` | Cortex | Long-term semantic storage (ChromaDB) |
| `amygdala` | Amygdala | Importance scoring |
| `prefrontal` | Prefrontal Cortex | Query orchestration and retrieval |
| `dreamer` | Sleep consolidation | Hippocampus-to-cortex transfer |

When adding new features, consider which "brain region" they belong to and follow the existing separation of concerns.

## Questions?

Open an issue or start a discussion -- we're happy to help!
