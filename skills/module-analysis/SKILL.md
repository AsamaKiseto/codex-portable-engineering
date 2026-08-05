---
name: module-analysis
description: 分析陌生或正在变化模块的职责、调用方、依赖、不变量、契约和重构风险，并在需要时刷新长期 module doc。开始较大模块修改或怀疑 module doc 过期时使用。
---

# 模块分析

改变 ownership 或结构前，先建立以仓库证据为基础的 module model。

## Repository adapter gate

执行前从当前仓库根读取 `.agents/skill-adapters/module-analysis.md`，并要求以下章节非空：

- `适用仓库`
- `模块路由`
- `架构文档`
- `局部规则与契约`
- `验证`

adapter 缺失、不完整、仓库不匹配或指向不存在的路由或文档 owner 时停止。

## Workflow

1. 通过 adapter 的 path routing 解析目标模块，并读取最近的 local rules。
2. 追踪 public entrypoints、upstream callers、downstream dependencies、persisted boundaries，以及
   dynamic 或 framework entrypoints。
3. 识别模块拥有什么、相邻层不能推入什么，以及哪些 invariants 必须在重构后继续成立。
4. 记录理解 main flow 所需的最小 active-code files，以及风险最高的 ownership 或兼容边界。
5. 与当前 module、contract 和 flow docs 交叉核对。
6. 职责、依赖、不变量或风险变化时刷新已有 durable owner，不创建平行模块说明。
7. 运行 adapter 验证，并总结职责、external contract、边界和主要 refactor risk。
