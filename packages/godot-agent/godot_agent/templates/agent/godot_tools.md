## Godot Agent Tools

### Scene Tools
- `gd_scene_inspect(path)` — Inspect a .tscn file and return its structure.
- `gd_scene_edit(path, action, ...)` — Edit a scene. Actions: add_node, remove_node, set_property, connect_signal.

### GDD Tools
- `gd_gdd_read(project_root, story_id, section)` — Read stories, mechanics, or style guide.
- `gd_gdd_validate(project_root)` — Check that all GDD-referenced files exist and tests pass.

### Asset Tools
- `gd_asset_generate(project_root, asset_type, name, prompt, ...)` — Generate image/audio/model assets.

### Harness Tools
- `gd_harness_run(project_root, test_script, scene_path)` — Run GDScript tests or scene integration tests.

### Project Tools
- `gd_project_inspect(project_root)` — Analyze project structure, stats, and warnings.

## Tool Calling Strategy

1. **Inspect before editing** — Always call `gd_scene_inspect` before `gd_scene_edit`.
2. **Test after editing** — Call `gd_harness_run` after modifying scenes or scripts.
3. **Validate GDD** — Call `gd_gdd_validate` after completing a user story.
4. **Generate assets last** — Only generate assets after the scene structure is confirmed.
