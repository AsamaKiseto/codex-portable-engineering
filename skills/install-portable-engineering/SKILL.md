---
name: install-portable-engineering
description: 从 AsamaKiseto/codex-portable-engineering 的最新稳定 GitHub Release 首次安装、接管、检查或升级 Codex 用户级通用规则和全部 portable Skills。用户通过内置 skill-installer 从固定 tag 安装本入口后，在任意目录要求安装或更新 portable engineering、同步 ~/.codex/AGENTS.md managed block 或迁移无 receipt 的历史安装时使用；不需要消费仓库 pin，不跟随默认分支，不覆盖人工修改或其它来源的同名 Skill。
---

# 安装与更新 Portable Engineering

这是独立 source 的唯一用户入口。首次安装、历史接管、只检查和后续升级使用同一套 source
validation、ownership、digest、backup 和事务语义，不维护第二个 updater Skill。

## Source 与入口

- 唯一 source 是 private repository `AsamaKiseto/codex-portable-engineering`，通过已认证的
  GitHub CLI 访问。
- 默认选择 GitHub `releases/latest` 返回的稳定 Release；拒绝 draft、prerelease、无 tag Release，
  不跟随 `main`，也不读取当前工作目录的消费仓库 pin。
- Codex 根目录是 `${CODEX_HOME:-$HOME/.codex}`；拒绝空路径、文件系统根和 source checkout。
- 本 Skill 第一次通过 Codex 内置 `$skill-installer` 从明确稳定 tag 的
  `skills/install-portable-engineering` 安装。此后始终调用 `$install-portable-engineering`；不再
  安装或调用独立 updater。
- Skill 的显式调用授权本 source 的用户级安装或升级。用户只要求检查时保持 read-only；显式指定
  历史 tag 导致降级时必须再次说明并取得确认。

private repository 认证失败时停止并提示配置 `gh auth` 或 GitHub SSH；不得回退到公开镜像、缓存
副本、默认分支或消费仓库 vendor copy，也不得输出 credential。

## Release 预检

1. 检查 `gh --version`、`gh auth status` 和 Codex 根路径。
2. 查询最新稳定 Release，在 Codex 根的本次唯一 staging 目录 shallow clone 其 tag。持有原子
   创建的 source lock；已有 lock 时报告另一个更新或待恢复事务，不并发写入。
3. 要求 checkout `HEAD` 是 tag 解析出的 commit，并验证根 `portable-source.toml`：
   - `format_version = 1`
   - `name = "codex-portable-engineering"`
   - `version` 与 tag `v<version>` 一致
   - `repository = "AsamaKiseto/codex-portable-engineering"`
   - `skills_dir`、`rules_dir`、`evals_dir` 是不含绝对路径或 `..` 的仓库相对目录
4. 拒绝 source tree 中的 symlink、越界路径、重复 Skill 名、目录名与 `SKILL.md` frontmatter
   `name` 不一致，以及缺失 `agents/openai.yaml` 的 Skill。目标 Release 必须包含本 Skill。
5. 读取 `<rules_dir>/rule-pack.toml`，验证 format、name、version、module 唯一性与所有 module 路径，
   按 manifest 顺序以单个空行连接 module 正文并计算 SHA256。

所有来源、现有安装和事务计划必须在第一次 durable write 前验证完毕。

## 目录摘要与 receipt

Skill tree digest 使用固定算法：进入目标 Skill 目录，拒绝 symlink，只枚举 regular files；以
`LC_ALL=C` 对 `./` 开头的相对路径做 NUL-safe 排序，对每个文件执行 SHA256，再对按序的
`<file-sha256><two spaces><relative-path>\n` 记录整体计算 SHA256。source、staging 和 installed
目录使用同一算法。

receipt 位于
`<codex-root>/portable-sources/codex-portable-engineering.json`，至少记录：

```json
{
  "format_version": 1,
  "source": {
    "repository": "AsamaKiseto/codex-portable-engineering",
    "version": "0.2.1",
    "tag": "v0.2.1",
    "commit_sha": "<40-hex>"
  },
  "rules": {
    "pack": "codex-engineering-baseline",
    "version": "1.0.0",
    "sha256": "<rendered-body-sha256>"
  },
  "skills": {
    "install-portable-engineering": {"tree_sha256": "<tree-sha256>"}
  }
}
```

写 receipt 时列出本 Release 的全部 Skills。字段只保存 source identity 和内容摘要，不保存 token、
环境变量、消费仓库路径或个人业务信息。

## 现有安装判定

### 已有 receipt

- 要求 format 和 repository identity 精确匹配。
- 对每个 receipt 登记且仍存在的 Skill，比对 installed digest 与 receipt digest。不同表示人工修改，
  整体停止并报告冲突；不得覆盖、merge 或只更新其它项。
- receipt 登记但本地缺失的 Skill 可以从目标 Release 恢复。当前 Release 新增且目标名不存在的
  Skill 可以安装；存在未登记同名目录时按 unmanaged 冲突停止。
- receipt 中存在但新 Release 已删除的 Skill 默认保持原位并报告 stale，不自动删除。唯一迁移
  例外是 `v0.2.0` 发布后被本统一入口取代的 `update-portable-engineering`：只有 receipt 或历史
  Release digest 能证明其未修改且属于本 source 时，才在同一事务备份后移除；否则停止并保留。
- 校验现有 managed rule block 的 header digest 与精确 body；不匹配时整体停止。

### 首次安装或 adoption

receipt 缺失时，不要求用户填写旧版本：

1. 查询 stable Release tags，并从新到旧读取可信发布内容。
2. 对目标 Release 将管理的每个已存在同名 Skill，寻找 tree digest 完全一致的历史稳定 Release。
   全部匹配后才接管；任一目录无法匹配时视为人工修改或其它来源，整体停止。
3. 对现有 `portable-rules` block 校验 header digest，再寻找 rendered body 完全一致的历史稳定
   Release。没有 block 时允许首次安装；结构损坏或无法匹配时停止。
4. 不检查也不登记 source stable Release 从未包含的其它用户级 Skills。
5. 若存在可证明未修改的历史 `update-portable-engineering`，按上文唯一迁移例外纳入备份与移除；
   无法证明来源时停止。
6. adoption 与目标安装在同一事务完成；成功前不提前写 receipt。

## 发布事务

用户只要求检查时，报告 installed version、target version、首次安装/adoption/update 计划和冲突；
不创建 backup，不修改规则、Skills 或 receipt。

执行安装或更新时：

1. 在 Codex 根同一文件系统准备完整 staging，重新核对每个 Skill digest 和规则 body digest。
2. 在 `<codex-root>/portable-sources/backups/<timestamp>-<old-tag>/` 保存本次将替换或移除的 Skill
   directories、原 `AGENTS.md` 和旧 receipt；只备份本 source 管理且实际改变的内容。
3. 逐个把旧受管 Skill rename 到本次 backup，再把完整 staged directory rename 到目标；不逐文件
   merge。本 Skill 自身最后替换。
4. 保留 `AGENTS.md` managed block 外的原始字节，以同目录唯一临时文件写完整新内容，flush、
   fsync、回读校验后 `os.replace`。
5. 全部目标校验通过后，以同样方式原子写 receipt。receipt 是事务最后的 commit point。
6. 任一步失败时按 backup 恢复本次已经切换的目标；只清理本次 staging 和 lock，保留不能自动
   恢复的 backup 并报告精确路径。不得触碰其它更新留下的目录。
7. 成功后重新计算 installed Skill digests、规则 body digest 和 receipt，确认与 Release 一致；
   报告 old/new tag、commit、安装/更新/恢复/stale 列表和 backup 路径，并提示重启 Codex。

## 边界

- 不读取或复制消费仓库 `.agents/skill-adapters/`；更新 adapter 不属于本 Skill。
- 不改写 `AGENTS.md` managed block 之外的个人规则，不修改其它 source 的 Skills。
- 除明确的 `v0.2.0` updater 合并迁移外，不自动删除、降级、merge 或解决本地修改。
- receipt 的 source identity、installed digest、Release 或 lock 状态不可信时 fail closed。
- 本 Skill 不 commit、push、发布 Release，也不修改消费仓库。
