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

首次使用时，通过 Codex 内置 `$skill-installer` 从明确稳定 tag 安装本仓库的单一 bootstrap：

```text
使用 $skill-installer 从
https://github.com/AsamaKiseto/codex-portable-engineering/tree/v0.2.0/skills/install-portable-engineering
安装 Skill
```

重启 Codex 后，在任意目录调用：

```text
$install-portable-engineering
```

它会安装全部 portable Skills、用户级规则 managed block 和 receipt。当前仓库为 private，消费机器
需要已配置 GitHub Git/SSH 访问凭据；安装不依赖任何消费仓库。

完成 bootstrap 后，可以在任意目录显式调用：

```text
$update-portable-engineering
```

该 Skill 直接查询本仓库最新稳定 GitHub Release，验证 tag、commit 和 source manifest，再安全
更新用户级 `AGENTS.md` managed block 与本 source 管理的 Skills。它用用户级 receipt 识别受管
内容；没有 receipt 的既有安装通过历史稳定 Release 的精确 digest 自动 adoption。人工修改、
其它来源同名目录、损坏 marker、draft/prerelease 和默认分支都不会被静默接受。

消费仓库 pin 继续服务可复现 bootstrap；日常用户级更新不要求先修改消费仓库参数。

## 适配边界

- Skill 的仓库适配使用消费仓库自己的 `.agents/skill-adapters/`。
- 规则适配使用 Codex 原生用户级、仓库根和目录级 `AGENTS.md` 继承链，不建立平行 rule-adapter
  schema。
- `evals/` 只用于发布前验证，不复制到 `${CODEX_HOME:-$HOME/.codex}/skills`。
- `update-portable-engineering` 只管理本 source 的用户级安装，不读取或更新消费仓库 adapter。
