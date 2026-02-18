# 朝会系统功能文档

## 系统概述

朝会系统是三国策略游戏的核心决策系统，模拟古代朝廷议事过程。整个游戏以皇宫全景地图（未央宫）为主界面，玩家通过点击不同宫殿处理各类政务。系统严格遵循东汉时期"君主只能控制身边之人，以此治理天下"的历史真实机制。

## 功能模块（按开发顺序）

1. [00_COURT_MEETING_OVERVIEW.md](00_COURT_MEETING_OVERVIEW.md) - 朝会系统总览
2. [03_COURT_MEETING_TOPICS.md](03_COURT_MEETING_TOPICS.md) - 朝会议题生成系统
3. [04_COURT_MEETING_MINISTERS.md](04_COURT_MEETING_MINISTERS.md) - 朝臣意见系统
4. [05_COURT_MEETING_DECISION.md](05_COURT_MEETING_DECISION.md) - 决策与结果系统
5. [06_COURT_MEETING_HISTORY.md](06_COURT_MEETING_HISTORY.md) - 朝会记录与历史评价
6. [07_AI_COURT_MEETING.md](07_AI_COURT_MEETING.md) - AI朝会系统
7. [08_COURT_MEETING_INTEGRATION.md](08_COURT_MEETING_INTEGRATION.md) - 朝会系统集成与优化

## 其他功能模块

- [数据模型设计](data_models.md) - 朝会系统数据模型设计
- [宫殿交互设计](palace_interaction.md) - 宫殿交互与状态管理
- [UI样式指南](ui_style_guide.md) - 朝会系统UI样式指南

## 技术架构

- **后端技术**：Python后端，使用JSON存储数据，发布-订阅模式处理事件
- **数据管理**：JSON存储朝会数据和宫殿状态
- **事件系统**：事件驱动的事务通知机制

## 核心设计原则

1. **历史真实性**：符合东汉末年的朝会制度和议事流程
2. **策略深度**：提供有意义的决策选择，影响游戏走向
3. **角色个性化**：不同朝臣有独特的性格和立场
4. **反馈明确**：决策结果清晰可见，便于玩家理解
5. **平衡性**：确保不同选项都有其价值和适用场景