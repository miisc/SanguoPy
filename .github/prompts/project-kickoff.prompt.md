你现在进入“项目启动理解 + 开发计划”模式。请严格遵守本仓库的 Copilot Instructions（Think Before Coding / tests-first / 闭环 / 手术式改动）。

背景材料：
- docs/design/GAME_VISION.md
- docs/design/CORE_SYSTEMS.md
- docs/design/OUT_OF_SCOPE.md
- docs/design/requirements.md
- docs/features/
- docs/design/technical specification.md

你的任务（按顺序输出）：

1) 需求理解摘要（尽量简短）
- 用你自己的话复述：产品目标、主要用户行为、关键约束。

2) 不确定点与澄清问题（强制）
- 列出 <=5 个不确定点
- 每个点给出 2 种可能解释 + 对实现/测试/架构的影响
- 给出对应澄清问题（<=5），按优先级排序（影响最大优先）

3) Feature 开发路线图（基于已有 features，可修改）
- 先给推荐的开发顺序（MVP -> 扩展）
- 每个 feature 输出：输入/输出、依赖、风险点、可验证成功标准（Pass/Fail）

4) Tests-first 计划（必须）
- 对每个 feature：先列出要写的最小测试用例（单元/集成/回归）
- 给出“验证命令/脚本”的建议路径（例如 tools/verify.ps1）
- 明确哪些测试必须先写才能开始实现

5) 闭环执行协议（必须）
- 你将如何执行：写测试 -> 实现 -> 跑验证 -> 读失败 -> 修复 -> 重跑
- 给出停止条件：通过 / 缺信息必须问 / 超过 N 次无进展需汇报阻塞与备选方案

注意：
- 在我回答第2部分问题前，不允许实现核心逻辑或大规模改动。