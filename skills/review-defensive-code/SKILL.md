---
name: review-defensive-code
description: 审查新增或修改代码中的无依据防御性编程，覆盖重复校验、静默吞错、默认值兜底、类型探测、自动降级和数值修补。完成实现、代码评审或用户要求禁止防御性编程时使用；提供只读 Python Git diff 检查脚本，其它语言进行语义审查。不用于无范围的全仓清理。
---

# 防御性代码审查

规则适用于所有语言与仓库。信任已确定的内部契约；直接实现需求，不为假设失败添加分支。
本 skill 不要求 repository adapter，不新增依赖。

## 界定范围

1. 读取有效 `AGENTS.md`、完整工作区状态和本次授权范围。保留其他人的修改；只读 review 不授权修复。
2. 确定比较基线和本次文件。脚本默认比较 HEAD 与当前工作区，包含暂存、未暂存及未忽略的未跟踪文件。
   存在其他人的改动时用 `--path` 限定文件，并人工区分同文件中的修改归属。
3. 只读检查只报告；已授权的实现或修复任务可以删除本次无依据分支。不顺手清理历史代码，不改业务契约，
   不为了消除告警而添加日志、helper、兼容层或 `noqa`。不自动启动 agent、改 CI 或发布评论。

## 检查新增 Python 模式

使用仓库要求的 Python 环境（Python 3.10+）运行相对此 SKILL.md 的 `scripts/check_defensive_diff.py`。
以下 `<skill-dir>` 指本 skill 的实际安装目录，`<repo>` 指目标仓库；脚本不写目标仓库。

```bash
python <skill-dir>/scripts/check_defensive_diff.py --repo <repo> --path src --path tests
python <skill-dir>/scripts/check_defensive_diff.py --repo <repo> --staged --format json
python <skill-dir>/scripts/check_defensive_diff.py --repo <repo> --base <merge-base-commit> --head <head-commit>
```

- `--base` / `--head` 比较两个确切快照，不自动求 merge-base。PR 检查需先用 Git 确认实际 merge-base；
  确保 checkout 包含两个提交。`--staged` 与 `--head` 互斥，默认 base 是 HEAD。
- `--path` 是仓库根相对的字面文件/目录路径，可以重复；不是 glob。重命名按新路径筛选。
- 对变动文件比较 owner 与 AST 模式的多重集合，纯注释、格式、行号变化和相同内容的重命名不算新模式。
  同一 owner 内移动相同模式不会再次报告；调用语境改变仍需人工审查。
- 返回 `1`：新出现 D001，或显式启用 `--fail-on-review` 后发现任何候选项。
- 返回 `2`：Git、读取、编码、Python 解析或冲突导致检查未完成；不得当作通过。
- 返回 `0`：没有满足阻断条件的模式。可能仍有候选项，不能称为“没有防御性代码”。

| 规则 | 处理 | 范围 |
| --- | --- | --- |
| D001 | 阻断 | 裸 `except`、`Exception` / `BaseException`（含 builtins 名称和元组）捕获后仅 `pass` |
| D101 | 语义审查 | `assert`、直接抛错的 `if` 分支 |
| D102 | 语义审查 | `.get(key, default)`、`getattr(obj, key, default)`、赋值/返回的 `x or default` |
| D103 | 语义审查 | 其它宽泛异常捕获，包括可能合理的清理再抛出 |
| D104 | 语义审查 | `nan_to_num`、`clamp`、`clip` 等数值替换或裁剪调用 |
| D105 | 语义审查 | `if` 条件内的 `isinstance`、`hasattr`、`getattr` |

这是有限的语法检查，未进行名称绑定、别名追踪、类型推断或控制流证明。D001 是明确的语法禁用项；
其它命中只作线索，不得按关键字删除合理代码。`except Exception: return None`、日志后继续等由 D103
提示并作语义判断。epsilon、重试、回退模型/设备等未必能被脚本识别，仍须读完整授权 diff。
非 Python 文件和非普通文件列入 `unscanned`；按语言和文件职责检查，不读取符号链接目标。

## 逐项判定必要性

阅读所在函数及最小必要调用方，回答：

- 删掉该分支，哪个当前调用、明确需求或可复现故障会失败？没有证据就不新增。
- 数据是否已由上游保证？索引、运算、标准库或框架自然报错是否已经足够？提前报错或美化信息本身不构成理由。
- 是否把非法状态改成默认值、空结果、静默跳过、降低精度或设备/算法降级，掩盖了真实失败？
- 是否属于有依据的外部输入/安全边界、资源释放、算法定义、可选配置默认值或既有失败隔离契约？
  这些职责可以保留，只在真实 owner 处处理一次，说明具体依据。

内部字段/类型/shape 的重复验证、推测性重试/兼容、随意 epsilon/裁剪等默认删除或不添加。
不能机械禁用 `if`、`raise`、`assert`、`isinstance` 或所有 `try`；普通业务分支不属于防御性编程。
不以“更加健壮”“以防万一”“未来可能需要”论证。无法从当前证据判断时明确未决点，不能把候选项当成已证实违规。

## 完成与门禁

报告范围、基线、脚本覆盖和未决项；保留的防御分支用一句话给出具体故障或契约依据。
修改后只运行相称的既有检查；只有实际改动或失败需要时重跑，避免重复审计。

本 skill 和用户级规则不能保证模型绝不写出违规代码。真正的合并阻断需要仓库 CI 执行此脚本，
再把对应 job 设为 required check；安装 skill 本身不会修改 CI 或远端保护。
CI runner 必须拿到固定、可审阅版本的脚本，不能假定作者机器的 `~/.codex/skills` 存在。
默认门禁仅阻断 D001；其余由 reviewer 结合证据判定。`--fail-on-review` 仅适用于团队明确采用的严格门禁，
不会自动辨别合理用法，也不提供可自签的忽略标记。
