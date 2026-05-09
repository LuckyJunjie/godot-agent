# Godot Agent 🤖🎮

An AI-powered agent for Godot 4.x game development, forked from [nanobot](https://github.com/HKUDS/nanobot).

Godot Agent lives inside your game project, understands GDScript and scenes, maintains a living Game Design Document, and can generate assets via LLM APIs — all through natural language conversation.

---

## ✨ Features

- **Scene Intelligence** — Parse, edit, and validate `.tscn` / `.tres` files with Godot's ClassDB
- **GDScript LSP** — Real-time code analysis, diagnostics, and refactoring via Godot's language server
- **MCP Integration** — Connects to `godot-mcp` (editor control), `godotiq` (scene intelligence), and `godogen` (code generation skills)
- **GDD Engine** — Structured Game Design Document with traceability: story → scene → script → test
- **Self-Harness** — Run GDScript unit tests and scene integration tests headlessly
- **Asset Pipeline** — Generate sprites, audio, and 3D models via CLI with LLM APIs
- **Multi-Channel** — CLI, WebSocket, WebUI, and chat apps (inherited from nanobot)

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/LuckyJunjie/godot-agent.git
cd godot-agent
pip install -e .
```

### 2. Initialize a Godot project

```bash
godot-agent init --project ./my_game
```

This creates:
- `gdd/` — Game Design Document structure
- `assets/` — Generated asset directories
- `tests/` — Test scaffolding

### 3. Configure

Edit `~/.godot-agent/config.json`:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "godot": {
    "editorPath": "/path/to/godot",
    "projectPath": "./my_game"
  }
}
```

### 4. Chat with your agent

```bash
godot-agent agent -m "Add a double-jump to the player character"
```

### 5. Generate assets

```bash
godot-agent asset generate image \
  --prompt "A pixel art slime enemy, 32x32, green" \
  --name "slime_enemy"
```

---

## 🏗️ Architecture

```
User Interface (CLI / WebUI / WebSocket)
         │
         ▼
nanobot Core Agent Loop
         │
         ▼
Godot Agent Kernel
    ├── scene/       — .tscn / .tres parser & editor
    ├── lsp/         — GDScript LSP client
    ├── gdd/         — GDD engine & traceability
    ├── harness/     — Headless test runner
    ├── assets/      — LLM asset generation
    └── godogen/     — Skill & template integrator
         │
    MCP Servers
    ├── godot-mcp    — Editor control
    ├── godotiq      — Scene intelligence
    └── godogen      — Code generation skills
```

See [`docs/godot-architecture.md`](./docs/godot-architecture.md) for full details.

---

## 📚 Documentation

| Topic | Document |
|---|---|
| Requirements | [`docs/godot-requirements.md`](./docs/godot-requirements.md) |
| Architecture | [`docs/godot-architecture.md`](./docs/godot-architecture.md) |
| MCP Integration | [`docs/godot-mcp-integration.md`](./docs/godot-mcp-integration.md) |
| LSP & Harness | [`docs/godot-lsp-harness.md`](./docs/godot-lsp-harness.md) |
| Scenes Design | [`docs/godot-scenes-design.md`](./docs/godot-scenes-design.md) |
| GDScript Design | [`docs/godot-gdscript-design.md`](./docs/godot-gdscript-design.md) |
| Assets Metadata | [`docs/godot-assets-meta.md`](./docs/godot-assets-meta.md) |
| Assets CLI | [`docs/godot-assets-cli.md`](./docs/godot-assets-cli.md) |

---

## 🧪 Testing

```bash
pytest                          # Run all tests
pytest tests/test_scene.py     # Run scene parser tests
pytest tests/test_harness.py   # Run harness tests
```

---

## 🤝 External Integrations

| Project | Repository | Role |
|---|---|---|
| godot-mcp | [satelliteoflove/godot-mcp](https://github.com/satelliteoflove/godot-mcp) | Editor control via MCP |
| godotiq | [salvo10f/godotiq](https://github.com/salvo10f/godotiq) | Scene intelligence |
| godogen | [htdt/godogen](https://github.com/htdt/godogen) | Skill templates |

---

## 📜 License

MIT — inherited from nanobot.

---

*Built with love for the Godot community.* 🎮
