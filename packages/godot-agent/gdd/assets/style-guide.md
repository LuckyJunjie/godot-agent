# Asset Style Guide

## Visual Style

- **2D pixel art**, top-down and side-view compatible
- **Resolution**: 32x32 for characters, 16x16 for items, 64x64 for bosses
- **Palette**: Limited 16-color fantasy RPG palette
- **Perspective**: Front/side for characters, top-down for environment
- **Animation**: 4-8 frames per action, 8-12 FPS

## Audio Style

- **SFX**: Retro 8-bit/16-bit chiptune style, crisp and short (<1s)
- **Music**: Orchestral chiptune hybrid, loop-friendly
- **Voice**: Text-only; no voice acting

## Prompt Template

```
2D pixel art game asset, {resolution}, {perspective},
fantasy RPG theme, limited 16-color palette, crisp edges,
no anti-aliasing, transparent background, game-ready
```

## Examples

| Asset | Prompt | Negative Prompt |
|---|---|---|
| Hero | "A brave knight in shining armor, idle pose" | "blurry, realistic, modern" |
| Slime | "A green jelly slime monster, bouncing" | "eyes, limbs, complex" |
| Potion | "A red glass healing potion with cork" | "label, text, background" |
