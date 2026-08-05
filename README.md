# Codex Portable Engineering

跨仓库复用的 Codex 工程规则和 Skills 版本化来源。

## 内容

| 路径 | 职责 |
| --- | --- |
| `skills/` | 可安装的通用 Skills |
| `rules/` | 写入用户级 `AGENTS.md` managed block 的 always-on rules |
| `evals/` | Skill 的开发期行为场景，不进入安装目录 |
| `portable-source.toml` | 发布包版本和目录 contract |

消费仓库的 repository adapter、路径、环境、测试命令、业务 contract 和 secret 不属于本仓库。

## 版本与消费

发布使用 SemVer tag。消费方应同时固定 tag 和 commit SHA，先校验
`portable-source.toml`，再从其中声明的 `skills_dir` 或 `rules_dir` 安装；不得直接跟随默认分支。

消费仓库可以提供 `$install-skills` 和 `$install-rules` bootstrap，负责拉取固定版本、验证
commit 和 source manifest，再写入 Codex 用户目录。当前仓库为 private，消费机器需要已配置的
GitHub 访问凭据。

## 适配边界

- Skill 的仓库适配使用消费仓库自己的 `.agents/skill-adapters/`。
- 规则适配使用 Codex 原生用户级、仓库根和目录级 `AGENTS.md` 继承链，不建立平行 rule-adapter
  schema。
- `evals/` 只用于发布前验证，不复制到 `${CODEX_HOME:-$HOME/.codex}/skills`。
