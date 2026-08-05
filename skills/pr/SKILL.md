---
name: pr
description: Review local staged, unstaged, and untracked changes, form coherent commits, run repository checks, publish a pull request, and monitor it until ready or blocked. Use only when the user explicitly asks to publish or manage a PR; do not use for ordinary code edits or read-only review of an existing remote PR, and never merge without explicit authorization.
---

# Pull Request 工作流

通过仓库 adapter 发布已经 review 的本地修改。以实际 Git/forge 状态和新鲜检查证据为准，不猜测权限、分支或验证要求。

## Repository adapter gate

执行前从当前仓库根读取 `.agents/skill-adapters/pr.md`，并验证 YAML frontmatter：

- `adapter_version` 必须为 `1`，`skill` 必须为 `pr`，`repository` 非空。
- `repository_markers` 必须是非空的仓库相对路径列表，且每个路径均存在。
- `capabilities` 必须显式声明 `review`、`commit`、`push`、`create_pr`、`monitor`、
  `merge` 和 `cleanup_owned_branch`。

正文必须包含：`适用仓库`、`规则与权限`、`运行环境与临时路径`、`变更范围与提交策略`、
`验证矩阵`、`分支与发布`、`证据与恢复`、`监测与完成`。

缺少 adapter、版本不兼容、Skill 名不匹配、marker 无效或 requested capability 不为 `true` 时，
在对应动作前停止并报告具体缺项。Capability 只表示仓库支持该动作，不代表用户已经授权。

## 权限与状态

- 解析 base、scope、draft/ready、merge method 和 merge authorization；未指定值只能从 adapter
  取得。
- 发布请求授权 review、commit、push 和 create-PR 仍取决于 adapter capability；自动修复 review
  finding、merge、远端分支删除和保护设置变更需要各自明确授权。
- 开始时记录 repository root、normal/worktree/detached 状态、原始 branch、base/head SHA、完整
  working-tree 状态和已存在的同 head/base PR。

## Evidence dossier

维护一份任务内事实记录，供 review、PR body、监测和最终报告共同使用：

- base/head SHA、目标文件和需求或 contract 来源
- staged/unstaged/untracked 范围与排除项
- findings、commit grouping 和每个 commit 的目的
- check command、执行对象 SHA、exit code、摘要和未运行原因
- local/remote head、existing/new PR、URL 和当前 forge 状态
- blocker、恢复点、保留的 cache 或工作区状态

不要把主 Agent 的推测写成事实；独立 reviewer 可用时只给它 requirements、base/head 和原始
diff，不传递预设结论。

## Workflow

1. 验证 adapter、capabilities 和用户授权，建立 evidence dossier；混有无关修改时先收窄范围。
2. Review 完整目标 diff，按 correctness、contract、data-loss、security 和 test-blocking 排序。
   blocker 阻止发布；是否修复 finding 由用户原始修改授权决定，不能由 PR 请求自动扩张。
3. 按 intent、risk、rollback 和 verification boundary 决定 single/split commits，只 stage 已确认
   范围。
4. 创建 coherent commits，并记录最终 head SHA。任何 amend、rebase 或新 commit 都会使旧 head
   上的验证证据失效。
5. 在 adapter 环境运行验证矩阵。每个成功结论必须绑定本次执行的完整命令、最终 head SHA 和
   exit code；partial check 不得外推为全量通过。若只能看到失败而无法区分 pre-existing 与新增
   regression，明确标记未归因，不猜测责任。
6. 重新确认 working tree、local head 和 remote state。已有同 head/base PR 时复用；不得重复
   创建。Push 后确认 remote head 与 dossier 一致，再创建或更新 PR。
7. 监测 required checks、reviews、conversations、draft、conflicts、base divergence 和
   mergeability，直到 ready、超时或明确 blocked。
8. 只有用户明确授权、`merge: true`、最终 local/remote SHA 一致且所有 required gate 通过时才
   merge。只在 `cleanup_owned_branch: true` 且能证明分支/工作区由本流程创建时清理。

## 恢复规则

- Push 成功但 PR 创建失败：保留 branch/head，只重试 create-PR，不重复 commit 或 push。
- PR 已存在：更新或监测现有 PR，不创建重复 PR。
- Auth、rate limit、timeout 或 connector failure：报告最后成功状态和可恢复动作，不声称失败
  动作已完成。
- Head mismatch、failed required check、changes requested 或 conflict：停止在 blocked 状态。
- 任何阻塞都保留 adapter 要求的诊断证据；不得为“完成流程”而绕过检查。

## 输出

报告 findings、commit grouping、branch/commits、PR URL、checks 及其 subject SHA、reviews、
mergeability、最终状态和恢复点。只有存在本次新鲜证据时才能声称 ready、green 或 merged。
