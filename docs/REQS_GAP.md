# Godot-Agent 需求差距分析

## 已实现 (✓) - 1400+ 行

| 需求 | 模块 | 状态 |
|------|------|------|
| G1 | scene/ | ✓ 解析 .tscn |
| G2 | scene/ | ✓ 解析 .gd (基础) |
| G3 | scene/ | ✓ 解析 .tres |
| G4 | gdd/ | ✓ project.godot (基础) |
| G5 | harness/ | ✓ headless runner |
| H1 | gdd/ | ✓ GDD 存储结构 |
| H2 | harness/ | ✓ unit test runner |
| H3 | harness/ | ✓ scene test |
| L1 | lsp/ | ✓ LSP client (框架) |
| A1 | assets/ | ✓ Asset metadata |
| A5 | assets/ | ✓ Asset pipeline |
| A2 | assets/ | ✓ 图像生成 CLI |
| A3 | assets/ | ✓ 音频生成 CLI |
| M1-M5 | mcp/ | ✓ MCP 框架 |

## 未实现 (✗)

### P1 - 中优先
| 需求 | 说明 |
|------|------|
| L2 | go-to-definition |
| L3 | Diagnostics |
| H4 | GDD traceability |
| A4 | 3D 模型 CLI |
| A6 | Asset versioning |

### P2 - 低优先
| 需求 | 说明 |
|------|------|
| G6 | Export CLI |
| G7 | Addons |
| L4-L5 | Refactoring |
| H5 | GDD auto-sync |

---

更新: 2026-05-06