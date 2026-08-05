---
name: trace-provenance
description: Trace the authoritative source of a configuration value, data selection, persisted artifact, checkpoint fact, or runtime value through defaults, overrides, producers, serialization, loading, and consumers. Use when the user needs evidence for an actual run or a clearly marked possible chain; this skill is report-only and must not modify code, artifacts, or documentation.
---

# 权威来源追踪

从实际运行证据回答值或 artifact 来自哪里、为何被选中，以及最终由谁消费。默认且始终只读；
修复代码或同步文档必须作为后续独立任务授权。

## Repository adapter gate

执行前从当前仓库根读取 `.agents/skill-adapters/trace-provenance.md`，并验证 YAML frontmatter：

- `adapter_version` 必须为 `1`，`skill` 必须为 `trace-provenance`，`repository` 非空。
- `repository_markers` 必须是非空的仓库相对路径列表，且每个路径均存在。
- `capabilities` 必须显式声明 `report`、`read_runtime_artifacts` 和 `integrity_checks`；执行对应
  能力前其值必须为 `true`。

正文必须包含：`适用仓库`、`规则与证据`、`追踪域`、`运行身份、优先级与脱敏`、
`权威持久化事实`、`生产与消费路由`、`稳定契约与知识同步`。

缺少 adapter、版本不兼容、Skill 名不匹配、marker 无效或 required capability 不为 `true` 时
停止。Adapter 不能授予本 Skill 写入权限。

## 输入身份

追踪 actual run 前尽量绑定：

- run/artifact 的明确路径或稳定 ID
- 目标 field/key 和 observed value
- checkpoint、update、stage 或时间点
- schema/format version、digest 和 producer code revision（如果存在）

缺少足以唯一定位运行的证据时，只输出 `possible chain`，不得称为 actual provenance。

## Workflow

1. 从用户可见结果、目标 run 或 artifact 开始，列出所有候选来源，例如 default、config、
   environment、CLI、checkpoint/resume、runtime mutation 和 fallback。
2. 按 adapter 定义的 precedence 和持久化证据逐一排除候选；不要找到第一条合理路径就停止。
3. 逆向定位 authoritative producer，再正向追踪 normalization、override、derivation、
   serialization、loading 和最终 consumers。
4. 为每一跳记录分类 `default|persisted|override|derived|consumed`、证据位置，以及证据强度
   `observed|code-supported|assumed` 和置信度 `high|medium|low`。
5. 在组件边界核对 input、transform 和 output；必要时运行 adapter 允许的只读查询或完整性检查，
   不写入 run、cache、artifact 或仓库文件。
6. 区分 cache reuse、materialization、recomputation、fallback、schema migration 和 unconfirmed
   状态；校验可用的 schema version、digest/checksum、producer revision 和 manifest linkage。
7. 对 adapter 登记的 secret、credential、token、个人路径和敏感字段做脱敏；不得为了证明链路
   输出明文 secret 或无关个人信息。
8. 与 durable contracts 交叉核对。证据冲突时并列报告各自来源、影响和未决条件，不静默选择。
   文档缺口只报告应更新的 owner，不在本 Skill 中修改。

## Evidence ledger

默认用表格记录：

| 节点 | 分类 | 证据 | 强度 | 置信度 | 结论 |
| --- | --- | --- | --- | --- | --- |

最终输出 run identity、authoritative source 或 possible chain、完整链路、被排除候选、完整性结果、
最终 consumers、冲突、脱敏项和未确认点。不得把 inference 表述为 observed fact。
