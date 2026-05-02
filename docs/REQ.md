# Godot-Agent 项目需求文档

## 项目概述

**项目名称**: godot-agent  
**仓库**: https://github.com/LuckyJunjie/godot-agent  
**基于**: nano-bot (HKUDS/nanobot AI agent fork)  
**目标**: 构建专注于 Godot 4.x 游戏开发的 AI Agent

---

## ✅ 已有的文档（从远端获取）

| 文档 | 说明 |
|---|---|
| `docs/godot-requirements.md` | 需求规格 (F1-F5, G1-G7, M1-M5, L1-L5, H1-H5, A1-A6) |
| `docs/godot-architecture.md` | 技术架构，组件设计，数据流 |
| `docs/godot-mcp-integration.md` | MCP 集成指南 |
| `docs/README.md` | nano-bot 兼容的 agent 文档 |

---

## 🔄 需要新增/更新的需求

### REQ-NEW-001: 文档归档 (nano-bot 相关)
- [ ] 创建 `docs/nano-bot/` 目录
- [ ] 归档 nano-bot 核心文档（前缀 `nano-bot_`）
- [ ] 归档 assistant 相关文档

### REQ-NEW-002: MCP 集成扩展
- [ ] godotiq 完整集成
- [ ] godogen skills 集成

### REQ-NEW-003: Assets CLI 工具
- [ ] 图像生成 CLI
- [ ] 音频生成 CLI
- [ ] 3D 模型生成 CLI

### REQ-NEW-004: 场景模板
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
- ✅ 核心文档已获取 (docs/)
- ⏳ 等待派发给团队开发

---

**创建时间**: 2026-05-02
**项目路径**: `/home/pi/.openclaw/workspace/smart-factory/godot-agent/`