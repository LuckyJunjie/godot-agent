# Godot Agent Documentation

> AI-powered Godot 4.x game development agent, forked from nanobot.

---

## Quick Navigation

### Getting Started
| Document | Description |
|---|---|
| [`godot-requirements.md`](./godot-requirements.md) | Full requirements specification (F/G/M/L/H/A) |
| [`godot-architecture.md`](./godot-architecture.md) | Technical architecture, component design, data flow |
| [`DEVELOPMENT_PLAN.md`](./DEVELOPMENT_PLAN.md) | Phased implementation roadmap |

### Integration
| Document | Description |
|---|---|
| [`godot-mcp-integration.md`](./godot-mcp-integration.md) | MCP servers: godot-mcp, godotiq, godogen |

### Development
| Document | Description |
|---|---|
| [`godot-lsp-harness.md`](./godot-lsp-harness.md) | GDScript LSP client & self-harness system |
| [`godot-scenes-design.md`](./godot-scenes-design.md) | Scene structure, design patterns, edit tool |
| [`godot-gdscript-design.md`](./godot-gdscript-design.md) | GDScript style guide & design patterns |

### Assets
| Document | Description |
|---|---|
| [`godot-assets-meta.md`](./godot-assets-meta.md) | Asset metadata schema & prompt engineering |
| [`godot-assets-cli.md`](./godot-assets-cli.md) | Asset generation CLI reference |

### Archive
| Document | Description |
|---|---|
| [`archive/nano-bot/`](./archive/nano-bot/) | Original nanobot docs (prefixed with `nano-bot-`) |

---

## Project Structure

```
godot-agent/
├── godot_agent/          # Core Python package
│   ├── scene/            # .tscn / .tres parser
│   ├── lsp/              # GDScript LSP client
│   ├── gdd/              # GDD engine
│   ├── harness/          # Self-harness runner
│   ├── assets/           # Asset pipeline
│   └── godogen/          # Skill integrator
├── gdd/                  # Game Design Document
├── docs/                 # This documentation
├── tests/                # Test suite
└── work/                 # Agent work logs
```

---

## External Resources

- **godot-mcp**: https://github.com/satelliteoflove/godot-mcp
- **godotiq**: https://github.com/salvo10f/godotiq
- **godogen**: https://github.com/htdt/godogen
- **Godot Engine**: https://godotengine.org
