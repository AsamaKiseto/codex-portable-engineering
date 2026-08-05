# AGENTS.md

## 仓库职责

本仓库只维护可跨仓库复用的 Codex Skills、always-on rules 和对应开发期 eval。不得加入某个消费
仓库的 adapter、绝对路径、环境名称、测试命令、内部 contract、secret 或业务事实。

## 布局

- `skills/`：可安装 Skill 的版本化源码；目录名必须与 `SKILL.md` frontmatter `name` 相同。
- `rules/`：通用规则源码；`rule-pack.toml` 固定 module 顺序和 rule pack 版本。
- `evals/`：portable Skill 的开发期行为场景，不随 Skill 安装。
- `portable-source.toml`：整个发布包的版本与目录 contract。
- `update-portable-engineering` 可以固定本仓库的 canonical GitHub identity；其它 Skill 仍不得嵌入
  消费仓库事实。

## 变更要求

- 修改 Skill 时校验 `SKILL.md` 和 `agents/openai.yaml`，必要时同步同名 eval。
- updater 变更必须验证首次 historical-release adoption、receipt ownership、本地修改拒绝、规则
  managed block 保留和 self-update-last 事务顺序。
- bootstrap 只负责验证 source 并进入同 Release updater workflow，不复制 updater 的安装、
  adoption、receipt 或事务正文。
- 修改规则时保持规则与消费仓库事实分离，并重新校验精确渲染 SHA256。
- 发布使用 SemVer tag；已经被消费仓库固定的 tag 不得移动或重写。
- 消费仓库必须同时固定 tag 和 commit SHA，不跟随默认分支。
