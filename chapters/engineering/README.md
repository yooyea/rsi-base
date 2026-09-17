# 工程保障

指导项目把重要工程要求落实为有效机制，使项目能够持续完成需求、修复问题并交付版本。

## 选择准则

| 当前问题 | 阅读 |
| --- | --- |
| 字段、协议、需求或当前状态存在歧义 | [契约与事实](rules/contracts/authoritative-contracts.md) |
| 出现跨层调用或模块耦合 | [边界约束](rules/boundaries/enforce-boundaries.md) |
| 有检查，但新模块或新路径未被覆盖 | [保障范围](rules/coverage/complete-coverage.md) |
| 测试通过但用户仍遇到错误 | [可观察结果](rules/verification/observable-outcomes.md) |
| 有 CI，但不确定是否真正阻断合入 | [有效门禁](rules/integration/effective-gates.md) |
| 本地可用，打包或部署后不可用 | [交付产物](rules/delivery/verified-artifacts.md) |
| 同类错误反复出现，或检查成本不断上升 | [保障维护](rules/maintenance/maintain-assurances.md) |

## 落实方式

从当前任务出发，明确要保持的性质及其依据。读取已有保障，找出实际缺口；在最合适的边界补齐，验证能发现对应错误，再核实其进入真实执行路径。

例如，依赖方向适合结构检查，参数生效适合行为验证，运行产物适合安装或部署验证。一个检查只支持其覆盖范围内的结论。

直接复用项目现有记录与工具。[模板](../../templates/project-assurances.md)只在缺少记录载体时使用；[示例](../../examples/parameter-rendering.md)展示完整路径。

新增准则应有实际工程问题作为依据。更少但有效的保障，优于大量重复步骤。
