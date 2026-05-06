# Godot-Agent 需求差距分析

## 已实现 (✓) - 1174 行

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

## 未实现 (✗)

### P0 - 高优先
| 需求 | 说明 | 优先级 |
|------|------|--------|
| M1 | godot-mcp 集成 | Must |
| M2 | godotiq 集成 | Must |
| M3 | godogen MCP tools | Must |
| M4 | MCP transports | Must |
| M5 | MCP auto-register | Must |

### P1 - 中优先
| 需求 | 说明 | 优先级 |
|------|------|--------|
| A2 | 图像生成 CLI | Must |
| A3 | 音频生成 CLI | Should |
| H4 | GDD traceability | Should |
| L2 | go-to-definition | Should |
| L3 | Diagnostics | Should |

### P2 - 低优先
| 需求 | 说明 | 优先级 |
|------|------|--------|
| G6 | Export CLI | Should |
| G7 | Addons | Should |
| A4 | 3D 模型 CLI | Could |
| A6 | Asset versioning | Should |
| L4-L5 | Refactoring | Should |
| H5 | GDD auto-sync | Could |

---

## 下一步开发计划

1. **MCP 集成** (M1-M5) - P0
2. **图像生成 CLI** (A2) - P1
3. ** LSP 增强** (L2-L3) - P1

更新: 2026-05-06