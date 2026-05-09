# Godot Agent — LSP & Self-Harness for GDD

## 1. GDScript LSP Integration

### 1.1 Why LSP Matters

GDScript 2.0 is a gradually typed language. Without type information and symbol resolution, an AI agent operates blind. The LSP gives the agent:
- **Diagnostics**: Syntax errors, type mismatches, unused variables before they reach runtime.
- **Navigation**: Jump from a method call to its definition across the project.
- **Refactoring**: Rename a symbol everywhere safely.
- **Completion**: Understand available methods and properties on any typed variable.

### 1.2 Architecture

```
┌─────────────┐      TCP/WebSocket       ┌─────────────┐
│ Godot Agent │  ◄────────────────────►  │ Godot Editor │
│  LSP Client │      port 6005 (default) │  LSP Server  │
└─────────────┘                          └─────────────┘
       │
       ▼
┌─────────────┐
│ SymbolCache │  ← Indexed project symbols for fast lookup
└─────────────┘
```

### 1.3 Configuration

```json
{
  "godot": {
    "lspPort": 6005,
    "lspHost": "127.0.0.1",
    "lspAutoConnect": true,
    "lspFallback": true
  }
}
```

Godot LSP is enabled in Editor Settings under **Network > Language Server**.

### 1.4 LSP Client API

```python
class GDScriptLSPClient:
    async def connect(self) -> None
    async def disconnect(self) -> None
    
    # Diagnostics
    async def get_diagnostics(self, file: str) -> list[Diagnostic]
    
    # Navigation
    async def goto_definition(self, file: str, line: int, column: int) -> Location | None
    async def find_references(self, file: str, line: int, column: int) -> list[Location]
    async def hover(self, file: str, line: int, column: int) -> str
    
    # Refactoring
    async def rename(self, file: str, line: int, column: int, new_name: str) -> WorkspaceEdit
    
    # Symbols
    async def document_symbols(self, file: str) -> list[DocumentSymbol]
    async def workspace_symbol(self, query: str) -> list[SymbolInformation]
```

### 1.5 Fallback Mode

When Godot editor is not running, the agent falls back to:
1. **Regex parser**: Extract classes, functions, signals, exports from GDScript.
2. **Cached class_db**: Godot's built-in API signatures.
3. **Previous LSP index**: Last-known symbol locations from disk cache.

```python
class GDScriptFallbackAnalyzer:
    def parse_file(self, path: str) -> GDScriptModule:
        # Regex-based extraction
        ...
    
    def resolve_type(self, variable: str, context: str) -> str | None:
        # Best-effort type inference
        ...
```

---

## 2. Self-Harness System

### 2.1 Philosophy

The agent must verify its own changes. Every edit to a scene or script is followed by a harness run. This creates a tight feedback loop:

```
Edit → Harness → Pass / Fail → (Fail → Diagnose → Fix → Harness)
```

### 2.2 Harness Types

#### Unit Tests (GDScript classes)

Uses GUT (Godot Unit Testing) or a lightweight built-in runner.

```gdscript
# res://tests/test_player_movement.gd
extends GutTest

var Player = load("res://scripts/player.gd")

func test_double_jump():
    var player = Player.new()
    player.velocity = Vector2.ZERO
    player.jump()
    assert_true(player.is_jumping)
    player.jump()  # double jump
    assert_true(player.can_double_jump)
    player.free()
```

Agent runs:
```bash
godot --headless --script res://tests/test_player_movement.gd
```

#### Scene Tests

Load a scene, simulate frames, assert node state.

```gdscript
# res://tests/harness/test_main_menu.gd
extends SceneHarness

func test_play_button_navigates_to_level():
    var scene = load_scene("res://scenes/main_menu.tscn")
    var btn = scene.find_child("PlayButton")
    btn.emit_signal("pressed")
    await_simulate_frames(5)
    assert_current_scene_is("res://scenes/level_01.tscn")
```

#### Integration Tests

Multi-scene flows.

```gdscript
# res://tests/harness/test_game_flow.gd
extends IntegrationHarness

func test_full_round():
    await_navigate_to("main_menu")
    await_click("PlayButton")
    await_level_loaded("level_01")
    await_player_reached_goal()
    await_victory_screen_visible()
```

### 2.3 Harness Runner API

```python
class HarnessRunner:
    async def run_unit(self, test_script: str) -> TestResult
    async def run_scene(self, scene_path: str, harness_script: str | None) -> SceneResult
    async def run_integration(self, flow_script: str) -> IntegrationResult
    async def benchmark(self, scene_path: str, frames: int) -> BenchmarkResult
    
    # Batch mode for CI
    async def run_all(self, pattern: str = "res://tests/**/*.gd") -> TestSuiteResult
```

### 2.4 TestResult Schema

```json
{
  "type": "unit|scene|integration",
  "passed": true,
  "duration_ms": 420,
  "assertions": 5,
  "failures": [],
  "errors": [],
  "coverage": {
    "scripts": ["res://scripts/player.gd"],
    "lines_hit": 45,
    "lines_total": 60
  },
  "logs": []
}
```

---

## 3. GDD-Driven Harness

### 3.1 GDD as Test Spec

Each GDD story defines acceptance criteria. The GDD Engine auto-generates harness stubs:

```yaml
---
id: story-001
acceptance:
  - Player can move with WASD
  - Player collision respects tilemap
---
```

GDD Engine produces:
```gdscript
# tests/harness/auto/story_001_test.gd
extends SceneHarness

func test_acceptance_0_player_can_move_with_wasd():
    # TODO: implement
    pass

func test_acceptance_1_player_collision_respects_tilemap():
    # TODO: implement
    pass
```

The agent (or human) fills in the implementation. On subsequent GDD updates, the engine preserves existing test bodies and adds new stubs.

### 3.2 Traceability Enforcement

```python
class GDDValidator:
    def validate_story(self, story: GDDStory) -> list[Violation]:
        violations = []
        for scene_path in story.scenes:
            if not file_exists(scene_path):
                violations.append(Violation("missing_scene", scene_path))
        for test_path in story.tests:
            result = self.harness.run_unit(test_path)
            if not result.passed:
                violations.append(Violation("test_failed", test_path, result.failures))
        return violations
```

---

## 4. CI/CD Integration

### 4.1 GitHub Actions Example

```yaml
# .github/workflows/godot-agent-ci.yml
name: Godot Agent CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Godot Agent
        run: pip install -e .
      - name: Run harness
        run: godot-agent harness --all --project ./my_game
      - name: Validate GDD traceability
        run: godot-agent gdd validate --strict
```

### 4.2 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: godot-agent-harness
        name: Run Godot Agent Harness
        entry: godot-agent harness --changed
        language: system
        pass_filenames: false
```

---

## 5. Configuration

```json
{
  "godot": {
    "harness": {
      "autoRun": true,
      "autoRunDelaySec": 2,
      "testDir": "res://tests",
      "timeoutSec": 30,
      "gutAddonPath": "res://addons/gut",
      "coverageEnabled": true
    }
  }
}
```
