# godot-agent 开发任务 (einstein)

## 1. 项目概述
- **仓库**: https://github.com/LuckyJunjie/godot-agent
- **本地路径**: `/home/pi/.openclaw/workspace/smart-factory/godot-agent/`
- **目标**: 构建 Godot 4.x AI Agent (基于 nano-bot fork)

## 2. 需求分析

### 已有的组件设计 (见 `docs/godot-architecture.md`)
- `godot_agent/scene/` - Scene Model Parser (.tscn, .tres)
- `godot_agent/lsp/` - GDScript LSP Client
- `godot_agent/gdd/` - GDD Engine
- `godot_agent/harness/` - Self-Harness Runner
- `godot_agent/assets/` - Asset Pipeline
- `godot_agent/godogen/` - Godogen Integrator

### 需要实现的核心功能 (按优先级)

#### P0 (Must Have)
1. **M1**: Integrate `godot-mcp` (satelliteoflove) - Editor MCP server
2. **M2**: Integrate `godotiq` (salvo10f) - Scene/node intelligence
3. **M3**: Expose godogen skills as built-in MCP tools
4. **G1**: Parse and edit `.tscn` scene files
5. **G2**: Parse and edit `.gd` GDScript files
6. **G4**: Inspect project configuration
7. **G5**: Run Godot in headless mode
8. **L1**: GDScript LSP client
9. **H1**: Structured GDD storage
10. **A1**: Asset metadata schema

#### P1 (Should Have)
- A2: Image asset generation CLI
- A3: Audio/SFX generation CLI
- H2-H3: Self-harness tests

## 3. 目录结构

```
godot-agent/
├── godot_agent/          # Python package
│   ├── __init__.py
│   ├── scene/          # Scene Model Parser
│   ├── lsp/          # LSP Client
│   ├── gdd/          # GDD Engine
│   ├── harness/       # Harness Runner
│   ├── assets/       # Asset Pipeline
│   └── godogen/      # Godogen Integrator
├── docs/              # 需求文档
│   ├── godot-requirements.md
│   ├── godot-architecture.md
│   └── godot-mcp-integration.md
└── README.md
```

## 4. 验收标准
- [ ] MCP 工具可注册并列出
- [ ] 可解析 .tscn 文件
- [ ] 可解析 .gd 文件
- [ ] 可运行 headless godot
- [ ] GDD 目录结构创建
- [ ] Asset metadata schema 定义
- [ ] 单元测试通过

## 5. 参考
- `docs/godot-architecture.md` - 技术架构
- `docs/godot-requirements.md` - 需求清单