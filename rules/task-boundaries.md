## 任务边界与执行授权

- `answer`、`review` 和 `monitor` 默认只读；`change` 只授权用户要求的工作及其必要后果。只读分析、
  诊断或 review 不隐含外部写入、发布或修复授权。
- 对用户未点名的工作，只有存在 reachable evidence，且省略会导致当前 acceptance 失败时才实施；
  否则报告或 defer，不因未来可能有用而新增机制。
- 新增依赖必须取得显式授权；Stop That Shit Guard 已 armed 时还必须具有 `deps=allow` contract。
- 默认不启动 subagent；只有用户明确要求或任务明确授权时才委派。Stop That Shit Guard 已 armed 时
  还必须遵守有限 `agents=N` 预算。
- `files=` 只在完整 touched boundary 已知时使用。必要 caller、test 或 durable doc 不在边界内时，
  必须先扩展 contract，不得静默越界或省略必要工作。
- 通用规则不全局禁止 hash。Stop That Shit Guard 已 armed 时，窄任务保持默认 `hash=deny`；发布、
  provenance、integrity、安装包校验等明确以 digest/checksum 为 acceptance 的任务使用显式
  `hash=allow` contract。该授权只允许 hash，不授权写入、发布或扩大文件范围。
- Stop That Shit 是可选的外部 Guard；未安装、未 trusted 或未 armed 时只执行上述语义规则，不声称
  存在机器拦截。
