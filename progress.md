# SanguoPy Progress

## 当前阶段结论
- 项目主轴已冻结为“宫廷政治主导的三国策略游戏”。
- MVP 核心闭环已明确为：朝会决策 -> 执行反馈 -> 下月再决策。
- 当前工作模式采用 tests-first、闭环迭代、手术式改动。

## 已冻结需求

### 1. 时间与节奏
- 游戏按旬推进。
- 每月初一触发大朝会。
- 紧急朝会仅由重大军事事件或重大灾害事件触发。
- 紧急朝会触发后，立即中断当前执行阶段并进入紧急朝会。

### 2. 玩家权限边界
- 朝会内负责国家级核心决策。
- 朝会外仅允许军事与情报类临时指令。
- 朝会外临时指令必须消耗诏令权威。

### 3. 诏令权威
- 上限 100。
- 初始值 50。
- 每月初一恢复 5%，采用四舍五入，恢复后封顶 100。
- 不允许扣减为负数。
- 临时指令统一成本为 10。

### 4. 临时指令规则
- 仅允许 6 类白名单指令。
- 同类指令最短冷却 1 旬。
- 每旬可执行次数按诏令权威动态决定。
- 当前实现语义：按“该旬首次校验时的权威快照”计算本旬总配额。

### 5. 数值系统
- 五维基础数值统一为：military、economy、technology、public_order、diplomacy。
- 五维数值统一范围 0-100。
- 每次结算后裁剪到边界。

### 6. 事件系统
- MVP 重大事件共 10 个，采用通用模板优先。
- 事件冷却按 event_type 生效，不按 event_id。
- 紧急朝会重大事件量化判定已冻结。

### 7. 提案与 LLM
- MVP 阶段提案由规则模板生成。
- LLM 可以修改提案数值，但必须通过校验网关。
- 史实冲突以《三国志》为准。
- 锁定项：官制、地名、年代、人物生卒、重大事件。

### 8. 地图与情报
- 迷雾下仅显示城市名。
- 不显示归属、兵力、驻将等细节。

## 已完成的文档与配置
- docs/design/GAME_VISION.md
- docs/design/CORE_SYSTEMS.md
- docs/design/OUT_OF_SCOPE.md
- docs/design/EVENT_TEMPLATES_MVP.json
- docs/design/TEMP_COMMAND_POLICY_MVP.json
- docs/design/LLM_VALIDATION_POLICY_MVP.json
- docs/design/requirements.md 已与 CORE_SYSTEMS 对齐。
- docs/design/technical specification.md 命名已统一。

## 已完成的实现

### GameModel
- 新增五维数值结算裁剪能力：apply_dimension_effects。
- 新增 court_resources.zhaoling_authority 默认存储。
- 已接入月初诏令权威恢复逻辑。

### GameController
- 已实现临时指令配额计算：get_temp_command_quota。
- 已实现重大事件判定：is_major_emergency_event。
- 已实现紧急朝会中断入口：trigger_emergency_meeting。
- 已实现事件类型冷却判断：can_trigger_event / register_event_trigger。
- 已实现真实临时指令入口：issue_temp_command。
- 已实现临时指令执行顺序校验：execute_temp_command。
- 已实现策略驱动临时指令入口：issue_command_from_policy（自动推导白名单/触发/费用/冷却）。

### TempCommandPolicy（新增）
- src/game/temp_command_policy.py：从 docs/design/TEMP_COMMAND_POLICY_MVP.json 加载白名单策略。
- 提供 is_whitelisted / get_command_config / get_command_cost / get_command_cooldown / is_trigger_met 接口。
- 运行时直接读取 docs/design/，不需要复制到 data 层。

## 已完成的测试
- 新增规则契约与行为测试：src/test/unit/test_mvp_rule_contracts.py。
- 扩展 GameModel 测试：src/test/unit/test_game_model.py。
- 新增临时指令策略测试：src/test/unit/test_temp_command_policy.py（20 个测试）。
- 当前新增测试已全部通过。

## 当前验证状态
- 聚焦规则测试通过。
- GameModel 相关测试通过。
- TempCommandPolicy 加载与运行时接入测试通过（20/20）。
- 回归验证命令通过：powershell -ExecutionPolicy Bypass -File tools/verify.ps1 -SkipCoverage。
- 当前已知单元与集成测试基线为绿色（verify.ps1 已新增 MvpRuleContracts 与 TempCommandPolicy 套件）。

## 当前成功标准完成度
- 已完成：需求主轴冻结。
- 已完成：MVP 核心规则文档化。
- 已完成：诏令权威消耗与月初恢复闭环。
- 已完成：紧急朝会量化判定与中断入口。
- 已完成：事件按类型冷却。
- 已完成：tests-first 基础框架和回归验证路径。
- 已完成：白名单临时指令策略 JSON 接入运行时（issue_command_from_policy）。
- 已完成：F1 — 事件队列接入紧急朝会（push_event + 4 测试）。
- 已完成：F2 — 诏令权威月度恢复边界测试补全（4 边界用例参数化测试）。
- 已完成：F3 — 提案 dimension_effects 与五维数值结算联动（make_decision + make_monthly_decision）。

## 测试基线（harness engineering 闭环后）
- 总测试数：131（原 102，新增 29）
- GameModel: 26 | CourtMeeting: 31 | LLMIntegration: 23 | LlmValidationGateway: 4 | MvpRuleContracts: 22 | TempCommandPolicy: 20 | Integration: 5（含1 skip）

## 已完成 Feature Specs

### F1 — 事件队列接入紧急朝会
**Goal:** 向事件队列推入重大事件时，自动中断执行并进入紧急朝会。
**Success criteria:**
- `push_event({type:military/disaster, severity:major})` → `game_info.paused=True` 且 `meeting_active=True`。
- `push_event(非重大事件)` → paused 与 meeting_active 均不变。
**Constraints:** 不改 `trigger_emergency_meeting` / `is_major_emergency_event` 逻辑；不引入新外部依赖。
**Test idea:** `TestEventQueueTriggersEmergencyMeeting` — 推入各类事件，断言 paused/meeting_active 状态（4 用例）。

### F2 — 诏令权威恢复边界
**Goal:** 用测试锁定月初诏令权威恢复的全部边界行为。
**Success criteria:**
- 4 边界值断言全部通过：95→100，0→0，100→100（封顶），19→20（四舍五入）。
- 不新增生产代码。
**Constraints:** 不改 `_recover_monthly_zhaoling_authority` 逻辑。
**Test idea:** `TestZhaolingAuthorityRecoveryBoundaries` — `@pytest.mark.parametrize` 4 组，断言 advance_time 后的值。

### F3 — 提案 dimension_effects 结算联动
**Goal:** 朝会决策选项中的 `dimension_effects` 自动写入五维数值。
**Success criteria:**
- 含 `dimension_effects` 的选项被选中后，`game_data["dimensions"]` 按 delta 变化且裁剪到 [0, 100]。
- `make_decision` 与 `make_monthly_decision` 两路均生效。
**Constraints:** 不改 `apply_dimension_effects` 裁剪逻辑；不改朝会 UI 层代码。
**Test idea:** `TestCourtDecisionDimensionEffects` — 注入含 `dimension_effects` 的选项，触发决策，断言 dimensions（4 用例）。

### F4 — 事件模板接入紧急朝会决策链
**Goal:** `push_event` 携带已知 `event_id` 时，紧急朝会的议题和选项从 `EVENT_TEMPLATES_MVP.json` 加载，决策后 effects 写入五维数值。
**Success criteria:**
- `push_event({"event_id": "evt_border_alarm", ...})` → topic options 含"固守待援"/"主动出击"/"议和拖延"。
- `make_emergency_decision("A")` 后 dimensions 按 JSON option A delta 变化（military +8，economy -4）。
- 无 event_id 或未知 event_id → 回退随机议题，不破坏现有行为。
**Constraints:** 不改 `is_major_emergency_event` 判定逻辑；不改 `apply_dimension_effects` 裁剪逻辑；不改月度朝会路径。
**Test idea:** `TestEventTemplateInEmergencyMeeting` — push 已知/未知 event_id，断言 topic options 与 dimensions（4 用例）。

### F5 — LLM 提案校验网关
**Goal:** LLM 修改提案效果数值后，必须经过校验网关；校验失败时自动回退模板默认值并记录审计日志。
**Success criteria:**
- 幅度违规（单维 |delta| > 15）→ `fallback_applied=True`，`failed_rules` 含 `"magnitude"`。
- 平衡违规（全正无负，无代价）→ `fallback_applied=True`，`failed_rules` 含 `"balance"`。
- 结构违规（proposal 缺必填字段）→ `fallback_applied=True`，`failed_rules` 含 `"schema"`。
- 校验通过 → `effects=llm_effects`，`fallback_applied=False`，`audit_log` 含 `template_effects` / `llm_effects` / `timestamp`。
**Constraints:** 不改 `court_meeting.py` / `game_model.py`；历史校验 MVP 阶段为占位，不接实际史实数据库。
**Test idea:** `TestLlmValidationGateway` — 4 用例分别命中结构/幅度/平衡/通过路径，断言 `fallback_applied` 与 `failed_rules`。

---

### F6 — 迷雾数据层执行
**Goal:** `get_cities_for_player(faction)` 对非己方城市屏蔽 `faction` 与 `soldiers`，防止数据层泄露敌方情报。
**Success criteria:**
- 己方城市（`city["faction"] == faction`）→ 返回完整数据，`faction`/`soldiers` 均可见。
- 非己方城市 → `faction=None`，`soldiers=None`，`name` 仍可见。
- `get_cities()` 在调用后不受影响，仍返回原始完整数据（返回值是副本，不污染 `game_data`）。
**Constraints:** 不改 `get_cities()`；MVP 可见规则 `city["faction"] == faction`，不引入 VisibilityManager 依赖。
**Test idea:** `TestCityFogOfWar` — 5 用例：己方完整 / 敌方 faction=None / 敌方 soldiers=None / 敌方 name 可见 / get_cities() 不被污染。

### F7 — 朝会提案库扩充
**Goal:** 将 7 条硬编码议题替换为从 JSON 加载的 30 条议题，覆盖军事/经济/外交/内政 4 类，每条含 `dimension_effects`。
**Success criteria:**
- `CourtTopicLoader.load_topics()` 返回 ≥30 条议题。
- 每个类别 ≥6 条（military/economy/diplomacy/internal）。
- 每条议题的每个 option 均含有效 `dimension_effects`（至少 1 个非零维度）。
- `CourtMeetingSystem.topic_templates` 长度 ≥30。
**Constraints:** 不改 `make_decision` / `apply_dimension_effects` 裁剪逻辑；不改现有 `TestTopicTemplateValidity` 测试（`"effects" in opt` 仍需通过，JSON options 均含 `"effects": {}`）。
**Test idea:** `TestCourtTopicLibrary` — 4 用例：pool≥30 / 各类别≥6 / options 含 dimension_effects / cms.topic_templates≥30。

---

## 待办 Feature Specs

<!-- 格式：Goal / Success criteria / Constraints / Test idea，不写其他 -->

