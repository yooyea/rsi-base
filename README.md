# rsi-base

**指导项目通过「可靠的工程化」保障自我迭代。**

项目是主体，自我迭代是目标，可靠的工程化是保障。

rsi-base 指导项目识别重要的工程要求，把要求落实为有效保障，并在持续迭代中维护这些保障。目标是在明确目标和授权范围内，持续交付可信的变化，减少重复错误、返工和人工兜底。

## 从哪里开始

让执行者读取 [SKILL.md](SKILL.md)，再按当前任务进入[工程保障章节](chapters/engineering/README.md)。无需每次读取所有材料，也不强制每个任务生成新文档。

接入已有项目时，先读取当前协议、架构、测试、工作流与实际仓库规则，复用已有机制。选择一个实际保障缺口，建立检查、证明检查有效，并核实它是否真正作用于对应的合入或交付路径。

[项目保障记录模板](templates/project-assurances.md)可用于记录缺口和依据；已有合适载体时直接复用。

## 共同指导

| 项目需要保持的性质 | 对应准则 |
| --- | --- |
| 需求、协议和实现依据明确一致 | [准确的契约与事实](chapters/engineering/rules/contracts/authoritative-contracts.md) |
| 架构边界不被变更绕过 | [可执行的边界约束](chapters/engineering/rules/boundaries/enforce-boundaries.md) |
| 新增模块也受到工程保障覆盖 | [保障范围完整](chapters/engineering/rules/coverage/complete-coverage.md) |
| 验证能够发现真实行为错误 | [验证可观察结果](chapters/engineering/rules/verification/observable-outcomes.md) |
| 必要检查确实控制合入 | [有效的合入门禁](chapters/engineering/rules/integration/effective-gates.md) |
| 验证对象与实际交付物相符 | [验证交付产物](chapters/engineering/rules/delivery/verified-artifacts.md) |
| 保障机制随项目持续维护 | [维护工程保障](chapters/engineering/rules/maintenance/maintain-assurances.md) |

这些准则约束保障目标，不统一项目的语言、框架、部署平台或 Agent 编排方式。PR 门禁是重要载体，但不能替代正确的需求、设计与运行反馈。

## 案例与参考

[参数修改到图表生效](examples/parameter-rendering.md)展示从实际风险到验证与门禁的完整路径。这是示例，不是已执行的业务测试。

[Codex PR 门禁案例](references/codex-pr-gates.md)记录具体机制、源码版本与公开可见性的限制。案例不自动成为所有项目的强制规则。

## 本仓库验证

需要 Python 3.11 或以上版本，无第三方 Python 依赖。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_docs.py
```

检查仅覆盖本仓库的本地文档路径、Skill 基本元数据和准则必需章节。它不证明准则语义正确、外部链接在线、工程保障已实施或业务已通过验收。

## 当前边界

这是首版指导，尚未在业务项目验证效果。本仓库配置了文档 CI；CI 配置本身不代表 GitHub 规则集已启用强制阻断，需读取实际配置并验证。

rsi-base 不提供自动合并授权、不修改项目权限、不预设通用 CI 平台，也不承诺项目自主能力会因安装本仓库而自动增长。
