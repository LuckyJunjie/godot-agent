# AGENTS.md — Godot Agent

> Instructions for AI assistants working on this codebase.

---

## Project Context

This is **godot-agent**, a fork of [nanobot](https://github.com/HKUDS/nanobot) focused on Godot 4.x game development.

- **Primary language**: Python 3.11+ (agent), GDScript 2.0 (game code)
- **Test runner**: pytest with asyncio support
- **Package manager**: pip / hatch
- **Linting**: ruff (line-length 100, py311 target)

---

## Directory Structure

```
godot-agent/
├── godot_agent/          # Core package — add Godot-specific features here
│   ├── scene/            # .tscn / .tres parser & editor
│   ├── lsp/              # GDScript LSP client (TCP port 6005)
│   ├── gdd/              # GDD engine (markdown + YAML front-matter)
│   ├── harness/          # Headless Godot test runner
│   ├── assets/           # LLM asset generation pipeline
│   ├── godogen/          # Skill/template integrator
│   └── cli/              # CLI entry point
├── nanobot/              # Inherited core — modify only when necessary
├── gdd/                  # Game Design Document (runtime data)
├── docs/                 # Documentation
│   ├── archive/nano-bot/ # Original nanobot docs
│   └── godot-*.md        # Godot Agent docs
├── tests/                # pytest suite
│   ├── test_*.py         # New godot-agent tests
│   └── agent/...         # Old nanobot tests (may be broken)
├── CLAUDE.md             # Detailed AI assistant context
└── pyproject.toml        # Project config
```

---

## Coding Conventions

### Python
- Follow existing code style in `godot_agent/` modules.
- Use type hints everywhere.
- Prefer `pathlib.Path` over `os.path`.
- Async-first for I/O operations (LSP, asset generation, harness).
- Keep modules independent; `godot_agent/scene/` should not depend on `godot_agent/lsp/`.

### GDScript (when generating)
- Enforce type hints: `var health: int = 100`
- Use `@export` for tunable values
- Document public APIs with `##` comments
- Prefer composition over inheritance

### Tests
- New tests go in `tests/test_<module>.py`.
- Use `pytest-asyncio` for async tests.
- Current baseline: 60 tests at 70% coverage.
- Run: `python3 -m pytest tests/test_assets.py tests/test_gdd.py tests/test_godogen.py tests/test_harness.py tests/test_lsp.py tests/test_scene.py -q`

---

## Documentation Rules

- When adding a new module, create `docs/godot-<module>.md`.
- Update `docs/README.md` index.
- Archive old docs in `docs/archive/nano-bot/` with `nano-bot-` prefix.

---

## MCP & External Tools

The agent integrates with three external MCP servers:
- `godot-mcp` — editor control
- `godotiq` — scene intelligence  
- `godogen` — code generation skills

When implementing MCP features:
- Use nanobot's existing `mcp` tool infrastructure.
- Register new tools in the unified registry.
- Follow the tool naming convention: `mcp_*` for external, `gd_*` for native, `godogen_*` for skills.

---

## Common Commands

```bash
# Install in dev mode
pip3 install -e ".[dev]"

# Run new tests only
python3 -m pytest tests/test_assets.py tests/test_gdd.py tests/test_godogen.py \
  tests/test_harness.py tests/test_lsp.py tests/test_scene.py -q

# Run CLI
python3 -m godot_agent.cli --help

# Lint
ruff check godot_agent/
```
