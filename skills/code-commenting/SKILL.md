---
name: code-commenting
description: 审查或补充非平凡代码的注释与 docstring，重点说明设计意图、不变量、数据 shape、副作用、失败边界和兼容原因。实现或评审无法仅靠命名与类型直接理解的逻辑时使用。
---

# 代码注释

按仓库规则补充解释性注释，不为了证明注释合理而改变业务行为。

## Repository adapter gate

执行前从当前仓库根读取 `.agents/skill-adapters/code-commenting.md`，并要求以下章节非空：

- `适用仓库`
- `语言与风格`
- `兼容标记`
- `领域注释`
- `验证与知识同步`

adapter 必须提供可验证的仓库标识和有效引用。adapter 缺失、不完整、引用失效或属于其它
仓库时停止，并报告具体缺项。

## Workflow

1. 修改前检查 touched functions 及其相邻注释。
2. 函数承担控制流、契约转换、shape/unit 处理、持久化、同步、兼容、资源生命周期或失败恢复
   时，视为非平凡函数。
3. 使用函数级 docstring 或紧邻块注释说明职责、关键输入输出、不变量、副作用和失败敏感行为。
4. 只在代码无法直接表达原因或约束的逻辑块前增加简短步骤注释。
5. 修改已有复杂函数时检查整个 touched region；更新或删除失真注释，不只标注新增行。
6. 命中兼容或领域场景时应用 adapter 规定的标记和注释要求。
7. 运行 adapter 规定的验证与知识同步步骤。

## Avoid

- 逐行复述赋值、调用或分支。
- 给每个 trivial getter 或 passthrough 增加注释。
- 用注释掩盖不清晰 ownership 或无必要的 thin abstraction。
- 编造无法由代码或持久化证据确认的领域含义。
- 把本应留在代码附近或 durable contract 的设计原因只写在聊天中。
