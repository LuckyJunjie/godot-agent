# Godot-Agent 项目需求文档

## 项目概述

**项目名称**: godot-agent  
**仓库**: https://github.com/LuckyJunjie/godot-agent  
**基于**: nano-bot (HKUDS/nanobot AI agent fork)  
**目标**: 构建专注于 Godot 4.x 游戏开发的 AI Agent

---

## ✅ 已完成的文档

| 文档 | 说明 |
|---|---|
| `docs/godot-requirements.md` | 需求规格 (F1-F5, G1-G7, M1-M5, L1-L5, H1-H5, A1-A6) |
| `docs/godot-architecture.md` | 技术架构，组件设计，数据流 |
| `docs/godot-mcp-integration.md` | MCP 集成指南 |
| `docs/godot-lsp-harness.md` | LSP 与 Self-Harness 文档 |
| `docs/godot-scenes-design.md` | 场景结构与设计 |
| `docs/godot-gdscript-design.md` | GDScript 设计规范 |
| `docs/godot-assets-meta.md` | 资源元数据与 Prompt 工程 |
| `docs/godot-assets-cli.md` | 资源生成 CLI 参考 |
| `docs/README.md` | 文档索引 |
| `CLAUDE.md` | AI Assistant 项目上下文 |
| `README.md` | 项目主 README |

## ✅ 已完成的归档

| 归档 | 说明 |
|---|---|
| `docs/archive/nano-bot/nano-bot-*.md` | nano-bot 原始文档（前缀归档） |

---

## 🔄 需要实现的功能

### REQ-NEW-001: MCP 集成扩展
- [ ] godotiq 完整集成
- [ ] godogen skills 集成

### REQ-NEW-002: Assets CLI 工具
- [ ] 图像生成 CLI
- [ ] 音频生成 CLI
- [ ] 3D 模型生成 CLI

### REQ-NEW-003: 场景模板
- [ ] 2D 游戏场景模板
- [ ] 3D 游戏场景模板

---

## 技术架构（已有文档摘要）

```
用户界面 → nanobot Core → Godot Agent Kernel
                              ├── Scene Model Parser
                              ├── GDScript LSP Client
                              ├── GDD Engine
                              ├── Self-Harness Runner
                              └── Asset Pipeline
```

**项目状态**:
- ✅ 仓库已 clone 到本地
- ✅ 核心文档已完成
- ✅ 基础 Python 模块已创建 (godot_agent/)
- ⏳ 等待继续开发实现

---

**创建时间**: 2026-05-02  
**项目路径**: `/Users/junjiepan/projects/godot-agent`
