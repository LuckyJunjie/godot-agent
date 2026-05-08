# Godot Agent

AI-powered agent for Godot 4.x game development, extending the [nanobot](https://github.com/HKUDS/nanobot) agent framework.

## Features

- **Scene Editing** — Parse and edit `.tscn` / `.tres` files programmatically
- **GDScript LSP Client** — Connect to Godot's built-in language server for go-to-definition, completion, and hover
- **GDD Engine** — Markdown + YAML front-matter game design documents with traceability validation
- **Asset Pipeline** — Generate image assets via DALL-E 3, Stability AI, or OpenRouter
- **Test Harness** — Run GDScript unit tests and scene load tests headlessly via Godot CLI
- **Godogen Skills** — YAML-based code generation templates (state machines, components, UI screens, input maps, animation trees)
- **Project Inspector** — Rich CLI report of any Godot project's scenes, scripts, autoloads, and stats

## Installation

```bash
pip install -e ./nanobot
pip install -e ./packages/godot-agent
```

## Quick Start

```bash
# Initialize a new Godot project with GDD scaffolding
godot-agent init ./my_game

# Inspect an existing project
cd my_game && godot-agent inspect

# Validate GDD traceability (story → scene → script → test)
godot-agent gdd-validate

# Generate an image asset
godot-agent asset generate "A pixel-art space pirate" --output assets/sprites/pirate.png

# Run tests
godot-agent harness tests/test_player.gd
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `godot-agent version` | Show version |
| `godot-agent init <path>` | Scaffold GDD, assets, tests, and config |
| `godot-agent inspect` | Rich project report |
| `godot-agent scene-inspect <path>` | Inspect a `.tscn` file |
| `godot-agent gdd-validate` | Check story→scene→script→test traceability |
| `godot-agent harness <script>` | Run GDScript tests headlessly |
| `godot-agent asset generate` | Generate an image asset |
| `godot-agent asset list` | List generated assets |
| `godot-agent config-show` | Show current configuration |

## Project Structure

```
packages/godot-agent/
├── godot_agent/
│   ├── scene/          # .tscn / .tres parser
│   ├── lsp/            # GDScript LSP client
│   ├── gdd/            # Game Design Document engine
│   ├── assets/         # Asset pipeline & image generation
│   ├── harness/        # Test harness runner
│   ├── godogen/        # Skill/code generation integrator
│   ├── inspector/      # Project inspector
│   ├── config/         # Configuration schemas
│   ├── bridge/         # Nanobot tool integration
│   ├── cli/            # Typer CLI
│   └── templates/      # GDScript & scene templates
├── tests/              # pytest suite (93 tests)
├── skills/godogen/     # YAML skill packs
├── examples/           # Example Godot projects
└── gdd/                # GDD runtime directory
```

## Architecture

Godot Agent extends nanobot's agent loop with Godot-specific tools:

- `gd_scene_inspect` — Read-only scene inspection
- `gd_scene_edit` — Edit scenes (add/remove nodes, properties, signals)
- `gd_gdd_read` — Read GDD stories
- `gd_gdd_validate` — Validate traceability
- `gd_asset_generate` — Generate assets
- `gd_harness_run` — Run tests

These tools are registered into nanobot's `ToolRegistry` and invoked by the LLM during the agent loop.

## License

MIT
