# Godot-Agent 开发流程文档

## 概述

输入需求 → 输出可运行游戏 (端到端自动化)

---

## 完整工作流

```
用户需求
   ↓
[1. 需求理解] → LLM/Mock 解析
   ↓
[2. GDD生成] → 游戏设计文档
   ↓  
[3. 代码生成] → GDScript + 场景
   ↓
[4. 验证] → 语法检查
   ↓
[5. 输出] → 游戏文件 (+截图)
```

---

## 各阶段详情

### 1. 需求理解 (RequirementLLM)

**输入**: 自然语言需求
```
"制作一款特别的贪食蛇游戏"
```

**处理**:
- Mock: 规则匹配 (贪食蛇 → snake)
- Real LLM: MiniMax API 智能理解

**输出**: `Requirement` 对象
```python
{
    "name": "neon_snake",
    "genre": "snake", 
    "features": ["wall_wrap", "neon_effects"],
    "core_mechanics": ["移动", "碰撞", "得分"]
}
```

---

### 2. GDD生成 (GDDEngine)

**输入**: Requirement 对象

**处理**: 
- 创建 `gdd/` 目录结构
- 生成 `index.md` (主文档)
- 生成 `stories/story-XXX.md` (具体故事)

**输出**: 
```
gdd/
├── index.md           # 项目索引
└── stories/
    └── story-001.md # 游戏设计
```

---

### 3. 代码生成 (CodeGenerator + GodogenIntegrator)

**输入**: GDD + 需求

**处理**:
- 分析游戏类型 (snake/platform/puzzle...)
- 生成 GDScript 脚本
- 生成 TSCN 场景

**输出**:
```
scripts/
└── snake.gd         # 游戏逻辑 (~50行)
scenes/
└── game.tscn         # 场景定义
```

---

### 4. 验证 (GameValidator)

**输入**: 生成的代码

**检查**:
- 语法检查 (extends, func/end)
- 场景检查 ([gd_scene])
- Godot 检查 (如果可用)

**输出**: `ValidationResult`
```python
{
    passed: bool,
    message: str,
    screenshot: str
}
```

---

### 5. 输出 (最终交付)

**目录结构**:
```
项目目录/
├── scripts/          # GDScript 文件
├── scenes/           # 场景文件
├── gdd/              # 游戏设计文档
├── screenshots/       # 截图 (如果Godot可用)
└── test_report.md    # 测试报告
```

---

## 模块清单

| 模块 | 位置 | 功能 |
|------|------|------|
| `workflow/llm.py` | 需求理解 | RequirementLLM |
| `workflow/real_llm.py` | LLM集成 | MiniMax API |
| `workflow/enhanced.py` | 增强工作流 | 带LLM的完整流程 |
| `workflow/validate.py` | 验证 | GameValidator |
| `workflow/test_fix.py` | 自动修复 | FixLoop |
| `godot_agent/scene/` | 场景解析 | SceneDocument |
| `godot_agent/gdd/` | GDD引擎 | GDDEngine |
| `godot_agent/godogen/` | 代码生成 | GodogenIntegrator |
| `godot_agent/harness/` | 测试 | HarnessRunner |
| `godot_agent/assets/` | 资源 | AssetPipeline |
| `godot_agent/mcp/` | MCP集成 | MCPClient |

---

## 使用方法

### 方式1: CLI
```bash
python scripts/godot_agent_cli.py generate-image --prompt "游戏需求"
python scripts/godot_agent_cli.py test
```

### 方式2: Python API
```python
from godot_agent.workflow import AgentWorkflow

workflow = AgentWorkflow("./my_game")
files = workflow.run("制作一款特别的贪食蛇游戏")
```

### 方式3: 增强模式 (带LLM)
```python
from godot_agent.workflow.enhanced import EnhancedWorkflow

workflow = EnhancedWorkflow("./my_game")
result = workflow.run_with_llm("游戏需求")
```

---

## 配置

### MiniMax API

```bash
# 设置环境变量
export MINIMAX_API_KEY='你的key'

# 或创建 minimax.json
echo '{"api_key": "your-key"}' > minimax.json
```

---

## 测试

```bash
# 运行所有测试
python -m pytest tests/ --cov=godot_agent

# 端到端测试
python tests/e2e_test.py
```

---

## 当前状态

- **代码行数**: ~1900 行
- **模块数**: 8+ 个
- **测试覆盖率**: 70%+
- **状态**: 核心功能可用

---

*更新: 2026-05-07*