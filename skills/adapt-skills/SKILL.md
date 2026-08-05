---
name: adapt-skills
description: 分析当前仓库的真实规则、路径、环境、测试、文档和权限边界，为一个或多个需要 repository adapter 的 portable Skills 生成或更新同名 adapter。用户要求让通用 Skill 适配当前或其它本地仓库、初始化 adapters、迁移 adapter gate 或检查 adapter 完整性时使用。本 Skill 是 adapter bootstrap，不要求自己的 repository adapter；不得凭猜测启用 capability。
---

# 适配仓库 Skills

根据目标 Skill 声明的 gate 和当前仓库证据生成窄 adapter。能适配的是结构与已确认事实，不是
未知的业务语义或权限。

## Scope

- 用户指定 Skill 时只处理这些 Skill；用户要求全部时，从用户级已安装 Skills 和当前仓库
  `.agents/portable-skills/` 中选择正文声明 `Repository adapter gate` 的 Skill。
- `adapt-skills` 自身不需要 adapter，避免 bootstrap 循环。
- 默认只写 `.agents/skill-adapters/`。只有用户同时要求建立持久路由时，才最小更新根
  `AGENTS.md` 或既有 adapter owner 文档。

## Workflow

1. 确认目标仓库根、完整 dirty worktree 和适用的 `AGENTS.md` 链；保留用户已有修改。
2. 逐个读取目标 Skill 的完整 `SKILL.md`，提取 adapter 文件名、支持的 gate version、必填
   frontmatter、capabilities、章节、拒绝条件和验证要求，不维护第二份通用 schema。
3. 只读检查仓库中与 gate 直接相关的证据：稳定仓库标记、运行环境、源代码 owner、测试配置、
   CI、durable docs、artifact/compatibility 规则和实际工具入口。不要全仓收集无关知识。
4. 为每个必填字段或章节建立 `observed|inferred|missing` 证据。`inferred` 必须在 adapter 中明确
   依据；`missing` 不得改写成肯定事实。
5. 新建 adapter 时只写仓库事实；更新既有 adapter 时局部合并，保留仍有效的人工约束，不用
   模板覆盖整个文件。
6. 验证 adapter 与目标 Skill 同名、gate version 受支持、所有 repository markers 和引用存在、
   必填章节非空、命令来自实际配置，并且没有 secret、个人绝对路径或其它仓库内容。
7. 报告每个 Skill 的 `ready|partial|blocked` 状态、证据来源、关闭的 capabilities 和仍需仓库
   维护者确认的项目。

## Adapter Rules

- 版本化 gate 完全遵循目标 Skill 声明。`repository_markers` 选择少量稳定、仓库相对、可验证的
  文件或目录；不使用 `.git`、cache、生成产物或个人路径。
- Capability 表示仓库具备实现条件，不表示用户已授权当次动作。没有直接证据或安全边界不清时
  写 `false`；不得为了让校验通过全部设为 `true`。
- 非版本化 gate 按目标 Skill 要求填充章节。缺少真实 owner、命令或 contract 时不创建一个
  看似完整的 adapter，而是保持 `blocked` 并列出所需输入。
- Adapter 只包含 repository-specific facts，不复制 portable workflow、通用工程规范或 Skill
  正文。
- PR、发布、删除、生产写入和 secret access 等高风险能力必须有仓库机制证据；即使 capability
  为 `true`，仍需当次用户授权。

## Validation

- 重新让目标 Skill 按自己的 gate 读取 adapter，确认它会接受已登记能力并拒绝未登记能力。
- 只修改 adapter 时不编造业务测试；运行仓库已有的规则/knowledge validation，或说明不存在。
- 不声称“适配任何仓库后一定可用”。缺少测试、docs、CI 或权限模型的仓库只能得到保守 adapter
  或明确 blocker。
