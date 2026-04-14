# 朝会议题导出清单

以下为当前代码中定义的议题模版及其位置标注（`has_location` 和 `related_city` / `related_position`）：

- **id:** tax_increase
  - **title:** 增税政策
  - **has_location:** False
  - **related:** None
  - **说明:** 全国性财政议题，不显示地图。

- **id:** military_expansion
  - **title:** 军事扩张
  - **has_location:** True
  - **related_city:** luoyang
  - **说明:** 与边境/国防相关，定位到都城/要塞以便地图聚焦。

- **id:** infrastructure
  - **title:** 基础设施建设
  - **has_location:** True
  - **related_city:** chengdu
  - **说明:** 地方性建设议题，显示并聚焦到目标城市。

- **id:** agricultural_development
  - **title:** 农业发展
  - **has_location:** False
  - **related:** None
  - **说明:** 宏观农业政策，不显示地图。

- **id:** trade_policy
  - **title:** 贸易政策
  - **has_location:** True
  - **related_city:** jianye
  - **说明:** 建议聚焦到通商口岸/港口城市（已标为 `jianye`）。

- **id:** education_reform
  - **title:** 教育改革
  - **has_location:** False
  - **related:** None
  - **说明:** 全国性制度性议题，不显示地图。

## 月度/紧急议题

- **id:** monthly_tax
  - **title:** 月度财政报告
  - **has_location:** False
  - **related:** None

- **id:** monthly_military
  - **title:** 月度军事报告
  - **has_location:** True
  - **related_city:** luoyang

- **id:** emergency_disaster
  - **title:** 自然灾害
  - **has_location:** True
  - **related_position:** [20, 12]

- **id:** emergency_border
  - **title:** 边境警报
  - **has_location:** True
  - **related_city:** luoyang

---

如需我将该清单导出为 JSON（用于自动化或测试），或将 `has_location` 检查集成到其他模块（例如日志、测试断言），我可以继续处理。 
