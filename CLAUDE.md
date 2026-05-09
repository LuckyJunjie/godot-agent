# CLAUDE.md — Godot Agent

> Context for AI assistants (Claude, Kimi, GPT, etc.) working on this codebase.

---

## 1. Project Identity

- **Name**: Godot Agent
- **Origin**: Fork of nanobot (HKUDS/nanobot) — a lightweight personal AI agent framework
- **Focus**: Godot 4.x game development automation
- **Language**: Python 3.11+ (agent), GDScript 2.0 (game code)

---

## 2. Architecture at a Glance

```
User Interface (CLI / WebSocket / WebUI)
         │
         ▼
nanobot Core Agent Loop (inherited, minimal changes)
         │
         ▼
Godot Agent Kernel (new)
    ├── scene/       — Parse & edit .tscn / .tres
    ├── lsp/         — GDScript LSP client (port 6005)
    ├── gdd/         — Game Design Document engine
    ├── harness/     — Headless Godot test runner
    ├── assets/      — LLM asset generation pipeline
    └── godogen/     — Skill/template integrator
         │
    MCP Servers (external)
    ├── godot-mcp    — Editor control
    ├── godotiq      — Scene intelligence
    └── filesystem   — Project file access
```

---

## 3. Key Conventions

### 3.1 Code Style
- Python: follow `pyproject.toml` ruff config (line-length 100, py311)
- GDScript: enforce type hints, PascalCase classes, snake_case functions
- Always preserve comments and ordering when editing `.tscn` / `.gd` files

### 3.2 Directory Layout
- `godot_agent/` — Core package. Keep it modular; each submodule is independent.
- `gdd/` — Game Design Document lives here. Markdown + YAML front-matter.
- `docs/` — Documentation. Archive nano-bot docs in `docs/archive/nano-bot/`.
- `tests/` — pytest. 60 tests at 70% coverage is the current baseline.

### 3.3 Editing Scenes & Scripts
- Treat `.tscn` as structured text (Godot's own format), not JSON.
- Always validate against ClassDB when setting properties.
- Always create `.bak` before overwriting scene files.
- Run harness after any edit to a scene or script.

### 3.4 MCP Integration
- MCP servers are configured in `config.json` under `tools.mcpServers`.
- Godogen skills are loaded as pseudo-MCP tools (no external server).
- Tool naming: `mcp_*` for external, `gd_*` for native, `godogen_*` for skills.

### 3.5 GDD Traceability
Every feature must trace:
```
GDD Story → Scene → Script → Test
```
The GDD Engine validates this automatically.

---

## 4. Common Tasks

### Add a new Godot-native tool
1. Define the tool class in `godot_agent/<module>/`
2. Add to tool registry (follow nanobot's registry pattern)
3. Add tests in `tests/test_<module>.py`
4. Document in `docs/godot-<topic>.md`

### Add a godogen skill
1. Create YAML skill file in `skills/`
2. Define `name`, `description`, `inputSchema`, `template`
3. `GodogenIntegrator.load_skill_pack()` auto-discovers it

### Regenerate an asset
1. Update the meta YAML in `assets/meta/`
2. Run `godot-agent asset regenerate <id>`
3. Verify scene references still valid

---

## 5. Testing

```bash
# Run all tests
pytest

# Run specific module
pytest tests/test_scene.py

# Run harness against a Godot project
pytest tests/test_harness.py --godot-project ./my_game
```

---

## 6. Important Files

| File | Purpose |
|---|---|
| `godot_agent/__init__.py` | Public API exports |
| `godot_agent/scene/__init__.py` | SceneDocument, ResourceDocument |
| `godot_agent/lsp/__init__.py` | GDScriptLSPClient |
| `godot_agent/gdd/__init__.py` | GDDEngine, GDDStory |
| `godot_agent/harness/__init__.py` | HarnessRunner, TestResult |
| `godot_agent/assets/__init__.py` | AssetPipeline, ImageMeta, AudioMeta, ModelMeta |
| `godot_agent/godogen/__init__.py` | GodogenIntegrator, ToolSpec |
| `docs/godot-architecture.md` | Architecture reference |
| `docs/godot-mcp-integration.md` | MCP setup guide |
| `gdd/index.md` | Project GDD root |

---

## 7. Gotchas

- **LSP protocol**: Godot LSP uses JSON-RPC over TCP, not stdio. Messages need `Content-Length` headers.
- **Headless Godot**: `--headless --script` exits after script finishes. Use `--main-pack` or custom main loop for scene simulation.
- **.tscn parsing**: Godot's text format is not formally specced. The parser is regex-based; edge cases may need manual handling.
- **Asset API keys**: Never commit keys. Use `${ENV_VAR}` in config.
- **nanobot compatibility**: We inherit nanobot's session, provider, and channel layers. Avoid modifying them unless necessary.
