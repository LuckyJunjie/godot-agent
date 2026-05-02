# Godot-Agent 开发计划

## Phase 1: 基础设施 (P0)

### 1.1 MCP 集成
- [ ] M1: godot-mcp 集成 (satelliteoflove)
- [ ] M2: godotiq 集成 (salvo10f)
- [ ] M3: godogen skills 暴露为 MCP tools

### 1.2 核心组件
- [ ] G1: .tscn 场景解析器
- [ ] G2: .gd GDScript 解析器
- [ ] G4: project.godot 配置检查
- [ ] G5: headless Godot 运行器
- [ ] L1: GDScript LSP 客户端

### 1.3 GDD & Assets
- [ ] H1: GDD 存储结构
- [ ] A1: Asset metadata schema

## Phase 2: 增强功能 (P1)

### 2.1 Asset 生成
- [ ] A2: 图像生成 CLI
- [ ] A3: 音频/SFX 生成 CLI

### 2.2 Self-Harness
- [ ] H2: GDScript 单元测试
- [ ] H3: Scene 集成测试

## 依赖
- godot-mcp: https://github.com/satelliteoflove/godot-mcp
- godotiq: https://github.com/salvo10f/godotiq
- godogen: https://github.com/htdt/godogen
