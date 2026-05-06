# Godot-Agent 自动化差距分析

## 目标: 端到端自动化

**输入**: 自然语言需求 (如 "开发贪食蛇游戏")  
**输出**: 可运行的游戏

---

## 现状 vs 期望

### 当前状态 (手动了大部分)

```
用户需求 → 我手动理解 → 手动创建GDD → 手动生成代码 → 我检查
                            ↑需要自动化                    ↑需要自动化
```

### 期望状态 (完全自动化)

```
用户需求 → godot-agent → 可运行游戏
              ↑
         AI 自动处理
```

---

## 差距定义

### G1: AI 理解需求
| 现状 | 期望 |
|------|------|
| 我理解需求，手动输入 | LLM 自动理解需求 |
| 我拆解功能 | AI 自动拆解 |
| 无 | 需求 → GDD 自动转换 |

**需要**: Prompt 模板 + LLM 集成

### G2: GDD 自动生成
| 现状 | 期望 |
|------|------|
| 手动创建 GDD 文档 | 自动生成 GDD 结构 |
| 手动写 acceptance | AI 自动推导 |
| 部分实现 | 完整 GDD Engine |

**需要**: GDD Auto-generator

### G3: 代码自动生成
| 现状 | 期望 |
|------|------|
| 手动调用 godogen | GDD → 代码自动映射 |
| 手动复制代码 | 自动写入文件 |
| 基础模板 | 完整场景+脚本生成 |

**需要**: Code Generator

### G4: 验证循环
| 现状 | 期望 |
|------|------|
| 我检查代码 | 自动解析检查 |
| 手动运行 Godot | 自动 headless 测试 |
| 手动发现问题 | AI 自动修复 |
| 无 | TDD 循环 |

**需要**: Auto-test + Self-fix

### G5: 交付
| 现状 | 期望 |
|------|------|
| 生成文件 | 自动导出 |
| 我 push | Auto push to remote |
| 无 | 可执行文件 |

**需要**: Auto-export

---

## 实现优先级

### P0 - 核心闭环
1. **需求理解** - 输入需求，输出 GDD
2. **代码生成** - GDD → 游戏代码
3. **验证** - 自动测试

### P1 - 增强
4. **多轮迭代** - 理解 → 生成 → 验证 → 修复
5. **完整性检查** - 所有文件关联

### P2 - 完善
6. **自动部署** - Push + Release
7. **文档生成** - Auto README

---

## 技术方案

### 核心组件

```python
class RequirementParser:
    """解析需求 → GDD"""
    def parse(self, user_input: str) -> GDD: ...

class CodeGenerator:
    """GDDP → 代码"""
    def generate(self, gdd: GDD) -> GameFiles: ...
    
class Validator:
    """验证 + 自动修复"""
    def validate(self, files: GameFiles) -> Report: ...

class AgentWorkflow:
    """主工作流"""
    def run(self, requirement: str) -> GameFiles:
        gdd = parser.parse(requirement)
        files = generator.generate(gdd)
        report = validator.validate(files)
        if not report.success:
            files = self.auto_fix(files, report)
        return files
```

### Agent System Prompt

```
你是 godot-agent，一个专业的游戏开发 AI Agent。

输入: 用户需求 (自然语言)
输出: 可运行的游戏

工作流程:
1. 理解需求，生成 GDD
2. 生成代码 (场景 + 脚本)
3. 验证代码
4. 如有问题，自动修复
5. 报告完成

你必须:
- 遵循 Godot 4.x 规范
- 生成完整可运行的游戏
- 自动处理所有中间步骤
- 只在无法解决时询问用户
```

---

## 待办

- [ ] P0: 核心闭环实现
- [ ] 测试: 贪食蛇完整自动化

更新: 2026-05-06