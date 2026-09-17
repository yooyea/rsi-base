# Codex PR 门禁：机制与可见性边界

研究记录日期：2026-09-17。

源码快照：`openai/codex@e269f2164cbb9f499e4f22301c393500e2a831f3`。本页来源于该日对公开源码、规则集、PR 和运行记录的读取；不代表之后的最新配置，也不是 OpenAI 内部流程的完整说明。

本页是案例，不能替代目标项目自己的[工程保障准则](../chapters/engineering/README.md)。未在此仓库执行 Codex 构建或测试。

## 可借鉴的具体机制

| 已观察机制 | 解决的风险 | 固定版本来源 |
| --- | --- | --- |
| 统一阻断工作流及汇总任务 | 必需检查集合分散，失败未正确汇总 | [blocking-ci.yml](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/workflows/blocking-ci.yml) |
| 汇总只接受上层依赖明确成功 | 取消、异常跳过被混同为通过 | [check_ci_results.py](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/scripts/check_ci_results.py) |
| 禁止 TUI 直接依赖或导入 core | 变更绕开指定架构边界 | [verify_tui_core_boundary.py](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/scripts/verify_tui_core_boundary.py) |
| 检查工作区配置与 lint 继承 | 新模块没有受到既定规范覆盖 | [verify_cargo_workspace_manifests.py](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/scripts/verify_cargo_workspace_manifests.py) |
| 检查 Bazel 与 Cargo lint 配置一致 | 不同构建路径执行不同要求 | [repo-checks.yml](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/workflows/repo-checks.yml) |
| SDK 对着本次源码构建的 CLI 验证 | 组件单独通过，组合却失败 | [sdk.yml](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/workflows/sdk.yml) |
| wheel 在另一虚拟环境安装后冒烟 | 依赖开发环境、漏打包默认运行时 | [sdk.yml](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/workflows/sdk.yml) |
| 作业结束检查工作区变化 | 检查时自动修改了未提交的内容 | [check-clean-worktree](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/actions/check-clean-worktree/action.yml) |
| 工作区例外不再使用时要求删除 | 历史允许清单只增不减 | [verify_cargo_workspace_manifests.py](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/scripts/verify_cargo_workspace_manifests.py) |
| 构建分片、缓存及 release 条件分支快检 | 保障成本压住迭代吞吐 | [bazel.yml](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/workflows/bazel.yml) |

Bazel 的 release 条件编译检查使用 fastbuild 并关闭 debug assertions，以发现仅位于 release 条件代码中的编译错误；不等同于执行完整 release 优化和全部运行验证。

源码中的文本导入扫描不证明所有依赖关系正确；工作区干净不证明构建完全可复现；SDK 冒烟不证明所有模型任务正确。例外机制不自动授权其他项目放宽已有约束。

## 检查执行与实际阻断要分开

当日[主干规则集]（动态来源，见下）读取结果包含 `CI required`、`cla`、至少一个批准和对应 code owner 审查；`strict_required_status_checks_policy` 为 false。不能据此声称每次合入前必然针对那一刻最新主干重验，也不能推断所有身份都没有旁路能力。

当日读取的 [PR #46125](https://github.com/openai/codex/pull/46125) 来自 `copyberry/codex-internal-to-codex-oss/...` 同步分支。以下时间均为 UTC：

| 事件 | 2026-09-17 时间 |
| --- | --- |
| PR 合并 | 05:24:08 |
| 公开 blocking-ci 运行创建、启动 | 05:24:12 |
| CI required 结束 | 05:41:36，failure |

来源：[PR 元数据](https://api.github.com/repos/openai/codex/pulls/46125)、[运行元数据](https://api.github.com/repos/openai/codex/actions/runs/35185597218)、[最终任务](https://github.com/openai/codex/actions/runs/35185597218/job/105090271558)。这些为动态公开记录，引用时应核实是否有后续重跑及新尝试。

这个样本没有等待这次公开检查完成再合入。无法从公开材料确认它此前经过哪些内部检查或具体授权路径。不能把同步 bot 身份等同于代码全部由 Agent 编写，也不能用一个样本推导整体失败率或失败归因。

[主干规则集](https://api.github.com/repos/openai/codex/rulesets/6735016)与[推送限制](https://api.github.com/repos/openai/codex/rulesets/21660955)为动态来源，记录的是研究当日读取结果，不受上述源码 SHA 固定。

## 门禁本身也在演进

[PR #30146](https://github.com/openai/codex/pull/30146)将阻断集合移入统一工作流，提交说明同时要求管理员同步修改仓库规则集。仅更改 YAML 并不完成配置生效。

[PR #38051](https://github.com/openai/codex/pull/38051)让必需检查使用合并候选版本，避免只验证 PR 分支而遗漏与主干变化的组合问题。[工作流策略](https://github.com/openai/codex/blob/e269f2164cbb9f499e4f22301c393500e2a831f3/.github/workflows/README.md)区分 PR 与主干后置检查。

合入后检查发现问题时的内部处置流程不在本次可确认范围内。其他项目采用后置检查时，需自行明确处置责任、发布约束及恢复路径。

## 对 rsi-base 的取舍

借鉴从具体风险到可执行保障的转化，以及验证保障覆盖、维护成本与实际生效路径的方法。

不复制平台矩阵、Rust 专属规范、同步 bot 旁路、例外清单或内部授权。优先让目标项目现有工具承载保障，不建设一套并行平台。

## 补充来源

[GitHub 状态检查说明](https://docs.github.com/en/pull-requests/reference/status-checks)：跳过的 job 可能被视为成功，因此需要理解平台实际判定。

[GitHub 必需检查排错](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)：最新提交、合并候选和检查事件的关系。平台行为可能更新，接入时读取现行说明。

[OpenAI Harness engineering](https://openai.com/index/harness-engineering/)描述将部分架构约束落实为机械检查的内部产品实践。该文章案例不等同于 Codex 公开仓库，也不证明本仓库方案已有效。
