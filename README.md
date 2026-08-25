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

## 可选任务 Guard

本仓库的 always-on rules 和 repository-adapted Skills 可以与外部
[`lennney/stop-that-shit`](https://github.com/lennney/stop-that-shit) Plugin 组合使用。Plugin 保持独立
source ownership，本仓库不复制其同名 Skill、不接管其更新，也不把 host adapter 当作 repository
adapter。需要 Guard 时固定稳定 tag 安装：

```bash
codex plugin marketplace add lennney/stop-that-shit --ref 0.1.0
codex plugin add stop-that-shit@stop-that-shit
```

重启 Codex 后在 CLI TUI 用 `/hooks` 检查并 trust `UserPromptSubmit` 和 `PreToolUse`。窄任务默认保留
`hash=deny`；release、provenance、integrity 和 portable install 等以 digest 为既有 acceptance 的任务
显式使用 `hash=allow`，该授权不扩展其它任务边界。

## 版本与消费

发布使用 SemVer tag。首次安装入口固定稳定 tag；入口自身校验最新稳定 Release 的 tag、commit
和 `portable-source.toml`，不得直接跟随默认分支。

首次使用时，通过 Codex 内置 `$skill-installer` 从明确稳定 tag 安装本仓库的单一 bootstrap：

```text
使用 $skill-installer 从
https://github.com/AsamaKiseto/codex-portable-engineering/tree/v0.3.0/skills/install-portable-engineering
安装 Skill
```

重启 Codex 后，在任意目录调用：

```text
$install-portable-engineering
```

同一个 Skill 会根据本地 receipt 和内容摘要自动选择首次安装、历史接管、检查或升级路径，并管理
全部 portable Skills、用户级规则 managed block 和 receipt；不再安装独立 updater。当前仓库为
private，消费机器需要已配置 GitHub Git/SSH 访问凭据；安装和更新不依赖任何消费仓库，也不要求
手动修改版本参数。人工修改、其它来源同名目录、损坏 marker、draft/prerelease 和默认分支都不会
被静默接受。

## 适配边界

- Skill 的仓库适配使用消费仓库自己的 `.agents/skill-adapters/`。
- 规则适配使用 Codex 原生用户级、仓库根和目录级 `AGENTS.md` 继承链，不建立平行 rule-adapter
  schema。
- `evals/` 只用于发布前验证，不复制到 `${CODEX_HOME:-$HOME/.codex}/skills`。
- `install-portable-engineering` 只管理本 source 的用户级安装，不读取或更新消费仓库 adapter。
