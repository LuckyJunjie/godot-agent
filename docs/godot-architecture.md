# Godot Agent — Technical Architecture

## 1. Design Principles

1. **Fork-friendly**: We inherit nanobot's lightweight agent loop; we add Godot-specific layers rather than rewriting core infrastructure.
2. **MCP-first**: All Godot-editor communication happens through MCP servers. The agent itself is MCP-native.
3. **Scene-as-code**: `.tscn` and `.tres` are treated as editable text artifacts, just like `.gd` scripts.
4. **GDD-driven**: The Game Design Document is not documentation — it is executable specification that drives scene generation and test harnesses.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Interfaces                                 │
│  CLI (godot-agent)   WebUI   WebSocket   Telegram/Discord/Slack (optional)  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         nanobot Core Agent Loop                              │
│  Session → Runner → LLM Provider → Tool Router → Results                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Built-in Tools      │  │   MCP Tool Servers    │  │   Godot-Specific     │
│  (web, shell, fs,    │  │  • godot-mcp          │  │   Tools               │
│   ask_user, cron,    │  │  • godotiq            │  │  • scene_edit         │
│   my, notebook)      │  │  • godogen (skills)   │  │  • gdscript_edit      │
│                      │  │  • filesystem         │  │  • project_inspect    │
│                      │  │  • custom servers     │  │  • asset_generate     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Godot Agent Kernel                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Scene Model │  │ GDScript    │  │ GDD Engine  │  │ Asset Pipeline      │ │
│  │ Parser      │  │ LSP Client  │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Self-Harness│  │ Project     │  │ Godogen     │  │ Memory (SOUL/USER/  │ │
│  │ Runner      │  │ Inspector   │  │ Integrator  │  │  GDD/MEMORY)        │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Godot Editor/       │  │   Headless Godot      │  │   LLM Asset APIs      │
│   Running Game (MCP)  │  │   (Export / Test)     │  │   (Image/Audio/3D)    │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

---

## 3. Component Design

### 3.1 Scene Model Parser (`godot_agent/scene/`)

Responsibility: Treat `.tscn` and `.tres` as structured editable documents.

```python
class SceneDocument:
    """In-memory representation of a .tscn file."""
    
    def load(path: str) -> SceneDocument
    def save(path: str) -> None
    
    # Node graph
    def get_node(path: str) -> SceneNode
    def add_node(parent: str, name: str, type: str, instance: str | None)
    def remove_node(path: str)
    def set_property(node_path: str, key: str, value: Variant)
    def connect_signal(from_path: str, signal: str, to_path: str, method: str, binds: list)
    
    # Diff / patch
    def diff(other: SceneDocument) -> ScenePatch
    def apply_patch(patch: ScenePatch) -> None
```

**Key design decisions:**
- Uses Godot's own text format (not JSON/XML) so `git diff` remains human-readable.
- Preserves comments and ordering where possible.
- Validates against Godot's built-in classDB via cached `class_db.json`.

### 3.2 GDScript LSP Client (`godot_agent/lsp/`)

Responsibility: Speak GDScript LSP protocol to Godot's built-in language server.

```python
class GDScriptLSPClient:
    """Async LSP client over TCP/WebSocket."""
    
    async def initialize(project_root: str) -> InitializeResult
    async def goto_definition(file: str, line: int, column: int) -> Location
    async def rename_symbol(file: str, line: int, column: int, new_name: str) -> WorkspaceEdit
    async def get_diagnostics(file: str) -> list[Diagnostic]
    async def completion(file: str, line: int, column: int) -> list[CompletionItem]
    async def hover(file: str, line: int, column: int) -> str
```

**Key design decisions:**
- Connects to Godot LSP on default port `6005` (configurable).
- Falls back to regex-based analysis if LSP is offline.
- Caches symbol index for large projects.

### 3.3 GDD Engine (`godot_agent/gdd/`)

Responsibility: Parse, validate, and synchronize the Game Design Document.

```
gdd/
├── index.md           # Master index with front-matter
├── stories/
│   ├── story-001-player-movement.md
│   └── story-002-inventory-system.md
├── mechanics/
│   ├── combat.md
│   └── crafting.md
├── world/
│   ├── levels/
│   └── characters/
└── assets/
    └── style-guide.md
```

Each story file uses front-matter:
```yaml
---
id: story-001
status: draft | approved | implemented | deprecated
scenes:
  - res://scenes/player.tscn
  - res://scenes/hud.tscn
scripts:
  - res://scripts/player.gd
tests:
  - res://tests/test_player_movement.gd
acceptance:
  - Player can move with WASD
  - Player collision respects tilemap
---
```

**Key design decisions:**
- Markdown + YAML front-matter: human-editable, LLM-friendly.
- GDD Engine validates traceability: every `scenes` entry must exist, every `tests` entry must pass.
- Dream memory integration: long-term project decisions are written back to `gdd/index.md` and `memory/MEMORY.md`.

### 3.4 Self-Harness Runner (`godot_agent/harness/`)

Responsibility: Run GDScript tests and scene integration tests headlessly.

```python
class HarnessRunner:
    """Runs tests using Godot's --headless --script mode."""
    
    async def run_unit(test_script: str) -> TestResult
    async def run_scene(scene_path: str, timeout: float) -> SceneResult
    async def run_gut_suite(suite_path: str) -> GutResult
    async def benchmark(scene_path: str, duration: float) -> PerformanceReport
```

**Test types:**
1. **Unit**: GDScript class tests (GUT or custom test runner).
2. **Scene**: Load scene, simulate frames, assert node state.
3. **Integration**: Multi-scene flow tests (menu → level → pause → resume).

### 3.5 Asset Pipeline (`godot_agent/assets/`)

Responsibility: Generate, import, and reference game assets.

```python
class AssetPipeline:
    """Orchestrates asset generation and Godot import."""
    
    async def generate_image(meta: ImageMeta) -> Path
    async def generate_audio(meta: AudioMeta) -> Path
    async def generate_model(meta: ModelMeta) -> Path
    
    def create_import_config(path: Path) -> None  # writes .import file
    def reference_in_scene(asset_path: Path, scene: SceneDocument, node_path: str)
```

**Asset metadata schema:**
```yaml
# assets/sprites/hero_idle.meta.yaml
prompt: "A 2D pixel art hero in idle pose, 32x32, front view, fantasy RPG style"
negative_prompt: "blurry, modern, realistic"
model: "dall-e-3"  # or "midjourney", "stable-diffusion-xl", etc.
resolution: [32, 32]
format: "png"
sprite_sheet:
  columns: 4
  rows: 1
  animations:
    - name: "idle"
      frames: [0, 1, 2, 3]
      fps: 8
tags: ["character", "hero", "overworld"]
version: 3
```

### 3.6 Godogen Integrator (`godot_agent/godogen/`)

Responsibility: Load godogen skill packs as MCP-native tools.

```python
class GodogenIntegrator:
    """Discovers godogen skills and registers them as agent tools."""
    
    def load_skill_pack(path: str) -> list[ToolSpec]
    def register_as_mcp_tools(tools: list[ToolSpec]) -> None
    
    # Example generated tools:
    # • generate_state_machine(name, states, transitions)
    # • generate_component(type, properties)
    # • generate_ui_screen(layout_spec)
```

---

## 4. Data Flow

### 4.1 User Request: "Add a double-jump to the player"

```
1. User message → Session
2. LLM decides tools:
   • gdd_read(story="player-movement")
   • scene_inspect("res://scenes/player.tscn")
   • gdscript_read("res://scripts/player.gd")
3. Agent returns context to LLM
4. LLM plans:
   • Edit GDD story: add "double-jump" acceptance criteria
   • Edit player.gd: add double_jump logic
   • Edit player.tscn: add DoubleJumpTimer node
5. Agent executes edits, runs harness tests
6. If tests pass → commit memory, reply success
7. If tests fail → return diagnostics to LLM for fix loop
```

### 4.2 Asset Generation: "Generate a fireball sprite"

```
1. User message → Session
2. LLM calls asset_generate_image(prompt=..., scene_target="...")
3. AssetPipeline:
   a. Calls image-gen LLM API
   b. Writes PNG to assets/sprites/fireball.png
   c. Generates fireball.png.import for Godot
   d. Optionally patches scene to reference new sprite
4. Agent runs scene harness to verify render
5. Reply with preview + scene diff
```

---

## 5. Configuration Schema (additions to nanobot config)

```json
{
  "godot": {
    "editorPath": "/Applications/Godot.app/Contents/MacOS/Godot",
    "projectPath": "./my_game",
    "lspPort": 6005,
    "headlessArgs": ["--headless", "--quit"],
    "exportPresets": ["Web", "macOS", "Windows Desktop"]
  },
  "tools": {
    "godot": {
      "enable": true,
      "allowSceneEdit": true,
      "allowGdscriptEdit": true,
      "autoRunHarness": true,
      "sandbox": true
    },
    "assets": {
      "imageProvider": "dall-e-3",
      "imageApiKey": "${IMAGE_API_KEY}",
      "audioProvider": "elevenlabs",
      "audioApiKey": "${AUDIO_API_KEY}",
      "outputDir": "assets/generated"
    }
  },
  "mcpServers": {
    "godot-editor": {
      "command": "godot",
      "args": ["--script", "addons/godot-mcp/server.gd"]
    },
    "godotiq": {
      "command": "npx",
      "args": ["-y", "@godotiq/mcp-server"]
    }
  }
}
```

---

## 6. Deployment Patterns

| Pattern | Use Case |
|---|---|
| **Local dev** | Agent runs alongside Godot Editor, LSP connected to editor |
| **CI headless** | Agent runs with `--headless` Godot, no editor, full harness |
| **Daemon mode** | `godot-agent gateway` for WebUI/team collaboration |
| **Asset farm** | Dedicated agent instance for batch asset generation |
