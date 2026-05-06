---
id: story-001
title: Neon Snake Game
status: draft
scenes:
  - res://scenes/main.tscn
  - res://scenes/game.tscn
  - res://scenes/game_over.tscn
scripts:
  - res://scripts/snake.gd
  - res://scripts/food.gd
  - res://scripts/game_manager.gd
tests:
  - res://tests/test_snake.gd
acceptance:
  - Snake moves with arrow keys
  - Food increases length
  - Collision detection works
  - Neon glow visual effect
  - Wall wrap-around mechanic
---

# Neon Snake - Game Design

## 1. Vision
经典贪食蛇 + 霓虹灯视觉效果 + 独特穿越墙壁玩法

## 2. Core Mechanics
- **移动**: WASD/方向键控制
- **吃食物**: 变长并得分
- **独特能力**: 穿越墙壁（每关3次）
- **道具**: 加速/减速/无敌

## 3. Visuals
- 霓虹灯发光效果
- 深色背景 + 亮色蛇身
- 粒子效果

## 4. UI
- 分数显示
- 剩余穿越次数
- 速度指示