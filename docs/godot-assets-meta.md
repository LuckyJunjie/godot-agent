# Godot Agent — Assets Metadata & Prompts

## 1. Asset Philosophy

Game assets are not binary blobs — they are **generated artifacts with provenance**. Every asset carries:
- The prompt that created it
- The model/version used
- The acceptance criteria it must satisfy
- A history of regenerations

This allows the agent to:
- Regenerate assets with improved prompts
- Batch-regenerate whole style families
- Audit asset origins for licensing

---

## 2. Metadata Schema

### 2.1 Image Asset Meta

```yaml
# assets/meta/hero_idle.meta.yaml
id: hero_idle_v3
prompt: >
  A 2D pixel art hero in idle pose, 32x32 pixels, front view,
  fantasy RPG style, transparent background, 4-frame animation
negative_prompt: >
  blurry, modern clothing, realistic proportions, background,
  watermark, text
model: dall-e-3
model_params:
  quality: hd
  style: vivid
resolution: [32, 32]
format: png
sprite_sheet:
  columns: 4
  rows: 1
  frame_size: [32, 32]
  animations:
    - name: idle
      frames: [0, 1, 2, 3]
      fps: 8
      loop: true
tags: [character, hero, overworld, pixel_art]
generated: 2026-05-02T10:00:00Z
version: 3
history:
  - version: 1
    prompt: "A hero character"
    issue: "too realistic, wrong size"
  - version: 2
    prompt: "Pixel art hero 32x32"
    issue: "missing animation frames"
```

### 2.2 Audio Asset Meta

```yaml
# assets/meta/sword_swing.meta.yaml
id: sword_swing_v1
prompt: >
  Fast whoosh sound of a sword swinging through air,
  medieval weapon, crisp and sharp, no background noise
model: elevenlabs-scribe
model_params:
  voice_id: sfx_default
duration: 0.5
format: wav
sample_rate: 44100
channels: 1
tags: [sfx, combat, sword]
generated: 2026-05-02T10:00:00Z
version: 1
```

### 2.3 3D Model Asset Meta

```yaml
# assets/meta/chest_loot.meta.yaml
id: chest_loot_v2
prompt: >
  Low-poly wooden treasure chest, slightly open with golden glow inside,
  stylized fantasy, game-ready, single mesh
model: trellis
model_params:
  poly_count: 500
  uv_unwrapped: true
format: glb
textures:
  - type: diffuse
    resolution: [512, 512]
  - type: normal
    resolution: [512, 512]
tags: [prop, loot, dungeon]
generated: 2026-05-02T10:00:00Z
version: 2
```

---

## 3. Prompt Engineering for Game Assets

### 3.1 Style Consistency Prompts

To keep a cohesive art style across assets, the agent prepends a **style anchor** to every prompt:

```text
[STYLE_ANCHOR]
2D pixel art game asset, 32x32 resolution, top-down perspective,
fantasy RPG theme, limited 16-color palette, crisp edges,
no anti-aliasing, transparent background
[/STYLE_ANCHOR]

[ASSET_PROMPT]
A wooden barrel with metal bands, slightly weathered
[/ASSET_PROMPT]
```

The style anchor is stored in `gdd/assets/style-guide.md` and editable by the user.

### 3.2 Negative Prompt Templates

Default negative prompts per asset type:

| Type | Negative Prompt |
|---|---|
| Sprite | blurry, realistic, photograph, text, watermark, modern objects |
| UI | cluttered, 3D perspective, photographic, text-heavy |
| SFX | background noise, music, speech, muffled, distorted |
| 3D | high-poly, photorealistic, untextured, overlapping faces |

### 3.3 Variation Prompts

For sprite sheets, the agent auto-generates frame prompts:

```yaml
base: "A hero in {pose}, 32x32 pixel art"
frames:
  - pose: "idle stance"
  - pose: "idle breathing frame 2"
  - pose: "idle breathing frame 3"
  - pose: "idle breathing frame 4"
```

---

## 4. Asset Pipeline States

```
┌─────────┐   generate   ┌─────────┐   import   ┌─────────┐   validate   ┌─────────┐
│  META   │ ───────────► │  RAW    │ ─────────► │ GODOT   │ ───────────► │ SCENE   │
│ (yaml)  │              │ (png)   │            │ (.import)│             │ (ready) │
└─────────┘              └─────────┘            └─────────┘              └─────────┘
     │
     ▼
┌─────────┐
│ PROMPT  │  ← LLM API call
│ HISTORY │
└─────────┘
```

---

## 5. Asset Catalog

The agent maintains an `asset_catalog.json` in the project root:

```json
{
  "version": "1.0",
  "assets": [
    {
      "id": "hero_idle_v3",
      "type": "sprite",
      "path": "assets/generated/sprites/hero_idle.png",
      "meta": "assets/meta/hero_idle.meta.yaml",
      "imported": true,
      "referenced_by": ["res://scenes/player.tscn"]
    }
  ]
}
```

This enables:
- Find unused assets
- Batch update references when an asset is regenerated
- Calculate total project asset memory footprint
