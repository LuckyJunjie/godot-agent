# Godot-Agent 开发计划

## Phase 1: 基础设施 (P0) — 进行中

### 1.1 MCP 集成
- [x] M1: godot-mcp 集成设计文档 (satelliteoflove)
- [x] M2: godotiq 集成设计文档 (salvo10f)
- [x] M3: godogen skills 暴露为 MCP tools 设计文档
- [ ] M1-impl: godot-mcp 实际集成
- [ ] M2-impl: godotiq 实际集成
- [ ] M3-impl: godogen skills 运行时注册

### 1.2 核心组件
- [x] G1: .tscn 场景解析器 (基础实现)
- [x] G2: .gd GDScript 解析器设计
- [x] G4: project.godot 配置检查设计
- [x] G5: headless Godot 运行器 (基础实现)
- [x] L1: GDScript LSP 客户端 (基础实现)
- [ ] G1-enhance: 完整场景编辑（信号、属性验证）
- [ ] G2-enhance: GDScript AST 编辑
- [ ] L1-enhance: LSP 全功能（重构、诊断）

### 1.3 GDD & Assets
- [x] H1: GDD 存储结构 (基础实现)
- [x] A1: Asset metadata schema (基础实现)
- [ ] H1-enhance: GDD 双向同步
- [ ] A1-enhance: 完整 Asset Pipeline

## Phase 2: 增强功能 (P1)

### 2.1 Asset 生成
- [x] A2: 图像生成 CLI 设计
- [x] A3: 音频/SFX 生成 CLI 设计
- [ ] A2-impl: 图像生成 CLI 实现
- [ ] A3-impl: 音频生成 CLI 实现

### 2.2 Self-Harness
- [x] H2: GDScript 单元测试设计
- [x] H3: Scene 集成测试设计
- [ ] H2-impl: GUT 集成
- [ ] H3-impl: 场景模拟测试

## Phase 3: 产品化 (P2)

- [ ] WebUI Godot 专用面板
- [ ] 一键导出游戏构建
- [ ] Asset 版本控制与回滚
- [ ] 多项目工作区支持

## 依赖
- godot-mcp: https://github.com/satelliteoflove/godot-mcp
- godotiq: https://github.com/salvo10f/godotiq
- godogen: https://github.com/htdt/godogen
