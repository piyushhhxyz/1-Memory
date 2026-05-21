# Contributing to OneMemory

Thanks for your interest in contributing to OneMemory! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/1-Memory.git
   cd 1-Memory
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Verify the setup:
   ```bash
   uv run onememory --help
   ```

## Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test them locally.

3. Commit with a clear, descriptive message:
   ```bash
   git commit -m "Add: brief description of the change"
   ```

4. Push and open a pull request against `main`.

## Project Structure

```
src/onememory/
├── brain/            # Core memory processing (cortex, hippocampus, amygdala, etc.)
├── consolidation/    # Memory consolidation (dreamer)
├── interceptor/      # Network interception (proxy, addon)
├── mcp_server/       # MCP server for Claude integration
├── cli.py            # CLI entry point
├── config.py         # Configuration
└── models.py         # Data models
```

## Guidelines

- **Keep changes focused.** One feature or fix per pull request.
- **Follow existing patterns.** Match the code style and conventions already in the project.
- **Write clear commit messages.** Use the imperative mood (e.g., "Add feature" not "Added feature").
- **Test your changes.** Make sure nothing is broken before submitting.

## Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/piyushhhxyz/1-Memory/issues) with:

- A clear title and description
- Steps to reproduce (for bugs)
- Expected vs. actual behavior

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
