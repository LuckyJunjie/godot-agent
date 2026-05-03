# Godot Agent — Assets CLI Reference

## 1. Overview

The Assets CLI provides commands to generate, import, and manage game assets using LLM APIs. It integrates with the Asset Pipeline (`godot_agent.assets`) and supports image, audio, and 3D model generation.

---

## 2. Commands

### 2.1 `godot-agent asset generate`

Generate a new asset from a prompt.

```bash
# Generate a sprite
godot-agent asset generate image \
  --prompt "A pixel art slime enemy, 32x32, green, transparent background" \
  --name "slime_enemy" \
  --resolution 32x32 \
  --model dall-e-3

# Generate audio SFX
godot-agent asset generate audio \
  --prompt "Retro 8-bit coin pickup sound, bright and cheerful" \
  --name "coin_pickup" \
  --duration 0.5 \
  --model elevenlabs

# Generate 3D model
godot-agent asset generate model \
  --prompt "Low-poly wooden treasure chest, game-ready" \
  --name "chest_loot" \
  --model trellis
```

**Flags:**

| Flag | Description | Default |
|---|---|---|
| `--prompt` | Generation prompt (required) | — |
| `--name` | Output file name without extension | `asset_{timestamp}` |
| `--model` | LLM model to use | from config |
| `--resolution` | Image resolution (WxH) | 256x256 |
| `--duration` | Audio duration in seconds | 3.0 |
| `--negative-prompt` | Negative prompt | from style guide |
| `--tags` | Comma-separated tags | — |
| `--scene` | Auto-reference in scene | — |
| `--dry-run` | Preview without generating | false |

### 2.2 `godot-agent asset batch`

Generate multiple assets from a YAML spec file.

```bash
godot-agent asset batch --spec assets/batch/level_1_sprites.yaml
```

Example spec:
```yaml
# assets/batch/level_1_sprites.yaml
style_anchor: "2D pixel art, 32x32, fantasy RPG"
negative_prompt: "blurry, realistic"
output_dir: assets/generated/level_1

assets:
  - name: goblin_grunt
    type: image
    prompt: "A green goblin warrior, aggressive stance"
    sprite_sheet:
      columns: 4
      animations:
        - name: idle
          frames: [0, 1, 2, 3]
          fps: 6

  - name: health_potion
    type: image
    prompt: "A red glass potion bottle with cork"

  - name: dungeon_ambience
    type: audio
    prompt: "Dark dungeon ambient loop, dripping water, distant chains"
    duration: 30
    loop: true
```

### 2.3 `godot-agent asset import`

Create Godot `.import` files for existing raw assets.

```bash
# Import a single file
godot-agent asset import assets/raw/hero.png --type texture

# Bulk import a directory
godot-agent asset import assets/raw/ --recursive --type texture
```

**Import types:**

| Type | Godot Importer | Use Case |
|---|---|---|
| `texture` | CompressedTexture2D | PNG, JPG, WEBP sprites |
| `audio` | AudioStreamMP3 / OGG | Music, SFX |
| `model` | Mesh / Scene | GLB, OBJ |
| `font` | FontFile | TTF, OTF |
| `tileset` | TileSet | PNG tile atlases |

### 2.4 `godot-agent asset list`

List all managed assets.

```bash
# All assets
godot-agent asset list

# Filter by type
godot-agent asset list --type sprite

# Filter by tag
godot-agent asset list --tag combat

# Show unused assets
godot-agent asset list --unused
```

Output:
```
ID                  TYPE      STATUS    REFERENCES  SIZE
hero_idle_v3        sprite    imported  1           12KB
slime_enemy_v1      sprite    raw       0           8KB
coin_pickup_v1      audio     imported  3           44KB
chest_loot_v2       model     imported  1           156KB
```

### 2.5 `godot-agent asset regenerate`

Regenerate an existing asset with a new prompt or model.

```bash
# Regenerate with improved prompt
godot-agent asset regenerate slime_enemy_v1 \
  --prompt "A pixel art slime enemy, 32x32, bright green, bouncing animation"

# Regenerate all assets tagged 'draft'
godot-agent asset regenerate --tag draft --model dall-e-3
```

### 2.6 `godot-agent asset delete`

Remove an asset and its metadata.

```bash
# Safe delete (warn if referenced)
godot-agent asset delete slime_enemy_v1

# Force delete (breaks scene references)
godot-agent asset delete slime_enemy_v1 --force
```

---

## 3. Configuration

Asset CLI behavior is controlled via `config.json`:

```json
{
  "assets": {
    "imageProvider": "dall-e-3",
    "imageApiKey": "${IMAGE_API_KEY}",
    "audioProvider": "elevenlabs",
    "audioApiKey": "${AUDIO_API_KEY}",
    "modelProvider": "trellis",
    "modelApiKey": "${MODEL_API_KEY}",
    "outputDir": "assets/generated",
    "metaDir": "assets/meta",
    "styleGuide": "gdd/assets/style-guide.md",
    "defaultResolution": [256, 256],
    "defaultAudioDuration": 3.0,
    "autoImport": true,
    "autoReference": false
  }
}
```

---

## 4. Provider-Specific Notes

### DALL-E 3
- Best for: clean, detailed illustrations
- Max resolution: 1024x1024
- Supports: `quality: hd`, `style: vivid/natural`

### Stable Diffusion XL
- Best for: artistic control, LoRA fine-tuning
- Requires: local or API endpoint
- Supports: negative prompts, img2img, inpainting

### Midjourney
- Best for: concept art, atmospheric scenes
- Note: Requires Discord bot integration; agent wraps via API proxy

### ElevenLabs
- Best for: voice, SFX with Scribe model
- Supports: voice cloning, sound effects generation

### Trellis
- Best for: game-ready 3D assets from text/image
- Output: GLB with textures

---

## 5. CI/CD Integration

Generate assets in CI:

```yaml
# .github/workflows/assets.yml
name: Generate Assets
on:
  push:
    paths:
      - 'assets/batch/**/*.yaml'
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install godot-agent
        run: pip install -e .
      - name: Batch generate changed specs
        run: |
          for spec in $(git diff --name-only HEAD~1 | grep '.yaml'); do
            godot-agent asset batch --spec "$spec"
          done
        env:
          IMAGE_API_KEY: ${{ secrets.IMAGE_API_KEY }}
```
