---
name: install-portable-engineering
description: 从 AsamaKiseto/codex-portable-engineering 的稳定 GitHub Release 首次安装或接管 Codex 用户级通用规则、全部 portable Skills 和后续更新入口。用户通过内置 skill-installer 安装本 bootstrap 后，要求从任意目录初始化 portable engineering、迁移无 receipt 的历史安装或补齐全局 Skills/rules 时使用；不需要消费仓库 pin，不复制 repository adapters，不覆盖人工修改。
---

# 安装 Portable Engineering

这是独立 source 的一次性全局 bootstrap。它只负责取得可信 Release 和进入同 Release 的 canonical
updater workflow，不维护第二套安装、receipt 或事务 schema。

## Source 与目标

- 唯一 source 是 private repository `AsamaKiseto/codex-portable-engineering`。
- 默认选择 GitHub `releases/latest` 的稳定 Release；拒绝 draft、prerelease、无 tag Release 和
  默认分支 snapshot。
- Codex 根目录使用 `${CODEX_HOME:-$HOME/.codex}`。本 Skill 可从任意工作目录调用，不读取当前
  仓库的 portable pin、adapter、路径、环境或业务 contract。
- 初次安装本 bootstrap 应使用 Codex 内置 `$skill-installer`，从明确稳定 tag 的
  `skills/install-portable-engineering` 路径安装；不要从 `main` 安装。

## Bootstrap 流程

1. 检查 `gh --version`、`gh auth status` 和 Codex 根路径；private repository 认证失败时停止，
   不输出 credential，也不回退镜像或缓存副本。
2. 查询最新稳定 Release，在 Codex 根的本次唯一 staging 目录 shallow clone 其 tag，并验证：
   - checkout `HEAD` 是 tag 解析出的 commit；
   - `portable-source.toml` 使用 `format_version = 1`；
   - `name = "codex-portable-engineering"`；
   - `repository = "AsamaKiseto/codex-portable-engineering"`；
   - manifest `version` 与 tag `v<version>` 一致；
   - `skills_dir`、`rules_dir` 和 `evals_dir` 是安全的仓库相对目录。
3. 要求已验证 checkout 包含
   `<skills_dir>/update-portable-engineering/SKILL.md` 和 `agents/openai.yaml`，目录名与 frontmatter
   name 必须为 `update-portable-engineering`。拒绝 symlink、越界路径和缺失 updater。
4. 完整读取该 Release 内的 updater `SKILL.md`，把本次已验证 checkout 作为它的 target Release，
   执行其现有安装判定、historical-release adoption、tree digest、rule managed block、backup、
   self-update-last 和 receipt-last 事务。不要重新选择另一个 Release，也不要复制这些流程到本
   Skill。
5. 成功后确认以下内容均来自同一 Release 并与 receipt 一致：
   - `<codex-root>/skills/` 下全部 source Skills，包括本 bootstrap 和 updater；
   - `<codex-root>/AGENTS.md` 的 `portable-rules` managed block；
   - `<codex-root>/portable-sources/codex-portable-engineering.json`。
6. 报告 Release tag、commit、首次安装或 adoption 结果、保留的非受管内容与 backup 路径，并提示
   重启 Codex。后续日常更新使用 `$update-portable-engineering`。

## 边界

- bootstrap Skill 的显式调用只授权用户级 portable 安装，不授权修改消费仓库、adapter、Git
  remote、PR 或 Release。
- 不覆盖 updater 判定为人工修改、unmanaged 或其它 source 的内容；不自动删除或降级。
- updater workflow 校验失败时保持现有用户级安装，不用本 Skill 自创简化 fallback。
- 本 Skill 自身已经安装且 receipt 有效时允许再次调用，但仍执行同一 updater workflow，不维护
  平行状态。
