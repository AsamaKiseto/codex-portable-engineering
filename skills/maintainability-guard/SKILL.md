---
name: maintainability-guard
description: Review or, when explicitly authorized, refactor a bounded code scope for reading locality, thin abstractions, ownership drift, stale references, and persisted-contract risk while preserving public and dynamic surfaces. Use for focused maintainability work or explicitly requested aggressive cleanup; do not use to expand ordinary feature work into unrelated refactoring.
---

# 可维护性 Guard

改善局部可读性和 ownership，不把减少行数、文件数或函数数当成成功标准。

## Repository adapter gate

执行前从当前仓库根读取 `.agents/skill-adapters/maintainability-guard.md`，并验证 YAML frontmatter：

- `adapter_version` 必须为 `1`，`skill` 必须为 `maintainability-guard`，`repository` 非空。
- `repository_markers` 必须是非空的仓库相对路径列表，且每个路径均存在。
- `capabilities` 必须显式声明 `review`、`apply`、`focused`、`aggressive` 和 `update_docs`。

正文必须包含：`适用仓库`、`规则与授权边界`、`基线、范围与变更策略`、`维护政策与指标`、
`Ownership 与受保护表面`、`审计入口`、`验证与文档同步`。

缺少 adapter、版本不兼容、Skill 名不匹配、marker 无效或 requested capability 不为 `true` 时，
在对应动作前停止。Capability 不替代用户对修改、扩大范围或更新文档的授权。

## 两个独立维度

- `action=review`：只报告，不修改。用户说 review、audit、分析或未明确授权修改时使用。
- `action=apply`：只在用户明确要求修改、重构、精简或 cleanup 时使用。
- `scope=focused`：默认，只覆盖指定 main flow、直接依赖和本次变更造成的 orphan/stale references。
- `scope=aggressive`：只有用户明确要求 broad/aggressive cleanup 时使用，仍不得越过授权 ownership。

组合分别校验 adapter capability；`review+aggressive` 不得因为范围广而隐式变成 `apply`。
默认本地完成，不应仅为获得第二意见启动 subagent；用户明确授权委派且 Stop That Shit Guard 已
armed 时遵守有限 `agents=N` 预算。Guard 生效时 `action=review` 对应 `review` contract，
`action=apply` 对应 `change` contract，不得自行切换模式。

## Baseline 与候选

1. 记录 main entrypoint、目标 diff/scope、现有 dirty state、相关 contracts/tests 和 before metrics。
2. 若基线检查已失败，保存 pre-existing failures；修改后只把新增或变化的失败归因于本次工作。
3. 候选分类为 `keep|inline|merge|delete|move|defer`，并标记 `high|medium|low` confidence。
4. `apply` 只自动处理 high-confidence 候选；medium 提出方案，low 或 contract 不明时 defer。

## Workflow

1. 从 diff-first scope 开始，不审计无关历史债务。允许越出 diff 的范围仅包括本次修改直接造成的
   orphan chain，以及已被本次行为变化写成错误信息的注释、文档或局部名称。
2. 保留 domain concept、invariant、lifecycle、protocol、validation、复杂算法、多调用方、
   side-effect boundary、静态类型约束或有效 test seam。
3. 修改 public API、CLI、callback、registry、reflection、serialization、adapter、migration、
   checkpoint 或 artifact surface 前，检查 static/dynamic references、tests、docs 和兼容要求。
4. 每个 pass 只处理一个主要 concern，例如 inline、ownership move 或 stale-reference cleanup；不要
   在同一 pass 同时大规模 rename、move、inline 和接口重写。
5. 不用更深嵌套、新 thin wrapper、新依赖或削弱测试换取表面简化。静态类型保护有独立价值，
   不因运行时无操作就删除。
6. 修改后只沿本次变更直接产生的链路搜索未引用 function/type/import/file 和失真说明，循环处理
   到没有新 orphan，或逐项 defer 并说明风险。
7. 运行 adapter 审计和最小测试，比较 baseline/post-change；失败、指标恶化或 protected surface
   不确定时停止扩张并保留可恢复 diff。
8. 只有 `update_docs: true` 且任务授权长期事实变化时才同步 durable docs。
9. mapped acceptance 已通过且直接 orphan/stale-reference sweep 不再产生新候选时停止，不再重复
   同类 search、test 或 review。

## 输出

报告 action/scope、各候选决定与 confidence、baseline/new failures、前后指标、protected surfaces、
orphan/stale-reference sweep、behavior change、tests、docs 和 deferred items。没有修改授权时不得用
“顺手修复”替代 review 输出。
