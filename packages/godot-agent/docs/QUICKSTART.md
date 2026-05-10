# Godot Agent - Quick Start

## 安装

```bash
pip install -e .
```

## 基本用法

### 1. 生成图像资源

```bash
python scripts/godot_agent_cli.py generate-image --prompt "A pixel art hero" --name hero
```

### 2. 生成音频资源

```bash
python scripts/godot_agent_cli.py generate-audio --prompt "Jump sound" --name jump
```

### 3. 列出资源

```bash
python scripts/godot_agent_cli.py list-assets --type sprite
```

### 4. 运行测试

```bash
python scripts/godot_agent_cli.py test
```

### 5. MCP 服务器管理

```bash
python scripts/godot_agent_cli.py mcp start
python scripts/godot_agent_cli.py mcp list
python scripts/godot_agent_cli.py mcp stop
```

## Python API

```python
from godot_agent import GDDEngine, AssetPipeline

gdd = GDDEngine("./my-game")
gdd.initialize()

assets = AssetPipeline("./my-game")
assets.initialize()

from godot_agent.assets import ImageMeta
import asyncio
meta = ImageMeta(prompt="A hero sprite")
path = asyncio.run(assets.generate_image(meta, "hero"))
```

## 项目结构

```
godot-agent/
├── godot_agent/
│   ├── scene/      # 场景解析
│   ├── lsp/       # LSP 客户端
│   ├── gdd/       # GDD 引擎
│   ├── assets/    # 资源管道
│   ├── harness/  # 测试运行器
│   ├── godogen/  # 代码生成
│   └── mcp/      # MCP 集成
├── scripts/       # CLI 工具
├── tests/        # 测试
└── gdd/          # 游戏设计文档
```