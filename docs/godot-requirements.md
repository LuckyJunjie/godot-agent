# Godot Agent — Requirements Specification

> Derived from nanobot fork. Focus: AI-powered Godot 4.x game development agent.

---

## 1. Vision

Build an AI agent that lives inside a Godot 4.x project workspace and can:
- Understand, edit, and generate GDScript, scenes (`.tscn`), resources, and assets.
- Communicate with a running Godot editor or headless instance via MCP.
- Maintain a living Game Design Document (GDD) as structured memory.
- Generate game assets (images, audio, 3D models) via LLM APIs and CLI commands.
- Self-test and self-harness scene logic without human intervention.

---

## 2. Functional Requirements

### 2.1 Core Agent Loop (inherited from nanobot)
| ID | Requirement | Priority |
|---|---|---|
| F1 | Maintain conversation sessions with context window management | Must |
| F2 | Tool-use loop: LLM decides when to call tools, agent executes | Must |
| F3 | Memory consolidation (short-term → long-term) for project state | Must |
| F4 | Multi-channel support (CLI, WebSocket, WebUI) | Must |
| F5 | Configurable LLM providers (OpenRouter, Anthropic, OpenAI, local) | Must |

### 2.2 Godot-Specific Tooling
| ID | Requirement | Priority |
|---|---|---|
| G1 | Parse and edit `.tscn` scene files (nodes, properties, signals, groups) | Must |
| G2 | Parse and edit `.gd` GDScript files with AST awareness | Must |
| G3 | Parse and edit `.tres` resource files | Must |
| G4 | Inspect project configuration (`project.godot`) | Must |
| G5 | Run Godot in headless mode for scene testing / CI | Must |
| G6 | Export game builds (Windows, macOS, Linux, Web) via CLI | Should |
| G7 | Manage Godot addons and dependencies | Should |

### 2.3 MCP Integration
| ID | Requirement | Priority |
|---|---|---|
| M1 | Integrate `godot-mcp` (satelliteoflove) for editor control | Must |
| M2 | Integrate `godotiq` (salvo10f) for scene/node intelligence | Must |
| M3 | Expose godogen skills as built-in MCP tools | Must |
| M4 | Support stdio and HTTP/SSE MCP transports | Must |
| M5 | Auto-discover and register MCP tools on startup | Must |

### 2.4 LSP & Code Intelligence
| ID | Requirement | Priority |
|---|---|---|
| L1 | Embed GDScript LSP client for code analysis | Must |
| L2 | Provide symbol lookup (go-to-definition) across project | Should |
| L3 | Diagnostics: parse GDScript errors/warnings from LSP | Must |
| L4 | Refactoring: rename symbol, extract method via LSP | Should |
| L5 | Type inference hints for GDScript 2.0 | Should |

### 2.5 GDD & Self-Harness
| ID | Requirement | Priority |
|---|---|---|
| H1 | Structured GDD stored as markdown + front-matter in `gdd/` | Must |
| H2 | Self-harness: run unit tests on GDScript classes | Must |
| H3 | Self-harness: run scene integration tests headlessly | Must |
| H4 | Trace requirements from GDD → scene → script → test | Should |
| H5 | Auto-update GDD when code changes (bidirectional sync) | Should |

### 2.6 Asset Generation
| ID | Requirement | Priority |
|---|---|---|
| A1 | Asset metadata schema: prompt, style, resolution, format, tags | Must |
| A2 | CLI command to generate image assets via image-gen LLM API | Must |
| A3 | CLI command to generate audio/SFX via audio-gen LLM API | Should |
| A4 | CLI command to generate 3D models via text-to-3D API | Could |
| A5 | Asset pipeline: generated → imported → referenced in scene | Must |
| A6 | Asset versioning and prompt history | Should |

---

## 3. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NF1 | Works with Godot 4.2+ (GDScript 2.0) |
| NF2 | Cross-platform: macOS, Linux, Windows |
| NF3 | Headless operation for CI/CD pipelines |
| NF4 | Extensible skill system (compatible with nanobot skills) |
| NF5 | Sandbox file operations to project workspace |
| NF6 | Graceful degradation when Godot editor is offline |

---

## 4. Requirement Traceability Matrix

```
GDD Story → Technical Architecture → Component → Scene → Script → Test Case
```

Every feature in the GDD must be traceable to:
- A system component
- One or more scenes
- One or more GDScript files
- At least one harness test

---

## 5. External Dependencies

| Dependency | Source | Purpose |
|---|---|---|
| `godot-mcp` | github.com/satelliteoflove/godot-mcp | Editor MCP server |
| `godotiq` | github.com/salvo10f/godotiq | Scene intelligence MCP |
| `godogen` | github.com/htdt/godogen | Skill templates / code generation |
| Godot 4.x | godotengine.org | Runtime & editor |
| GDScript LSP | Built into Godot | Code intelligence |

---

## 6. Out of Scope (v1)

- Visual Shader graph editing (text-only shader editing supported)
- C# / C++ module development
- Console export (Xbox, PlayStation, Switch)
- Multiplayer netcode generation
- VR/XR-specific tooling
