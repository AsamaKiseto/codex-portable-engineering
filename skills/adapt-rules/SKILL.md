---
name: adapt-rules
description: 分析当前或指定仓库的 Codex 规则链，把规则区分为用户级通用基线、仓库专用事实、目录局部约束和显式覆盖，并在有可靠证据时更新仓库 `AGENTS.md`。用户要求迁移、适配、精简、去重或审计仓库规则时使用；不创建平行 rule-adapter schema，也不把 prose rule 写入 command policy 文件。
---

# Adapt Rules

利用 Codex 原生 `AGENTS.md` 继承链适配任意仓库：用户级文件承载通用 baseline，仓库根和更近的
目录级文件承载 repository-specific 事实与覆盖。该 Skill 是规则适配 bootstrap，不要求自己的
repository adapter。

## 前置检查

1. 确认目标仓库根，检查 dirty worktree，保留用户已有修改。
2. 读取用户级 `AGENTS.md`、仓库根到目标路径之间的所有 `AGENTS.md`，以及这些文件明确引用的
   rules、workflows、knowledge map 和长期 policy owner。
3. 若仓库提供 portable rule manifest，一并读取；不得假设所有仓库使用同一目录布局。
4. 识别用户级 portable-rules marker，校验 header digest 与精确 body。
5. 用户级受管区块缺失、损坏或 digest 不匹配时，可以完成分类审计，但不得据此删除仓库重复项；
   报告先安装或修复通用规则。

## 分类模型

逐条记录来源、适用范围和证据，并归入一类：

- `common`：跨仓库稳定成立的编码、注释、兼容、验证或授权原则。
- `repository_specific`：仓库路径、环境、测试命令、owner、业务 contract、artifact、runtime、
  knowledge map 或发布流程。
- `local_override`：只对某个子树成立，应留在距离 touched path 最近的 `AGENTS.md`。
- `explicit_conflict`：仓库因真实约束需要覆盖用户级 baseline；保留在仓库层并写明原因和边界，
  依赖 closer-scope precedence 生效。
- `unknown`：证据不足。保留原位并报告，不以措辞相似为由移动或删除。

同一规则可以引用通用原则并在仓库层补充具体值，但不要复制通用正文。

## 适配流程

用户只要求分析时输出分类和建议，不写文件。用户明确要求适配、迁移、精简或执行时：

1. 先建立规则 inventory 和生效优先级，记录每条规则的 owner。
2. 仅当用户级受管区块 digest 有效，且仓库条目与其中规则语义完全等价、没有更窄范围或额外
   约束时，才从仓库层删除重复正文。
3. 将仓库路径、环境、测试、owner、contract、runtime 和完成标准保留在仓库根规则。
4. 将子系统不变量和 escalation trigger 保留或移动到最近的目录级规则；移动前检查所有受影响
   路径，避免缩小或扩大作用域。
5. 显式冲突保留为仓库 override，说明它覆盖哪项 baseline、为什么、适用范围和解除条件。
6. 更新规则发现、安装和 ownership 的既有 durable doc；既有 owner 能承载时不新建重复文档。
7. 校验最终 `AGENTS.md` 链：通用事实只有一个 owner，仓库事实不进入用户级 block，局部事实
   不上浮，引用路径真实存在。

## 不采用的结构

- 不创建平行 rule-adapter 目录；仓库和目录级 `AGENTS.md` 本身就是适配层。
- 不把 instruction prose 写入 `~/.codex/rules/*.rules` 或仓库 `.codex/rules/*.rules`；这些文件
  用于命令执行 permission policy。
- 不通过 custom prompt 伪造顶层 slash command。安装后的 Skill 可用 `$adapt-rules` 显式调用，
  并由客户端在可用时显示于 `/` 菜单。
- 不自动把新发现的仓库规则提升为通用规则。通用 pack 变更必须在其 source repository 单独审查、
  版本化并重新安装。

## 完成报告

报告以下内容：

- 读取的规则链和有效优先级；
- 每类规则及其 owner；
- 删除的精确重复项、保留的 repository/local override 和未决项；
- 用户级 managed block 的 pack、version、digest 状态；
- 修改的规则与 durable docs、执行的验证和未执行项；
- behavior changed、protected surfaces changed，以及是否发生全仓机械改写。
