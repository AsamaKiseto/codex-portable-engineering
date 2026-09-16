---
name: module-analysis
description: 分析陌生或正在变化模块的职责、调用方、依赖、不变量、契约和重构风险，并在需要时刷新长期 module doc。开始较大模块修改或怀疑 module doc 过期时使用。
---

# 模块分析

改变 ownership 或结构前，先建立以仓库证据为基础的 module model。

## Repository adapter gate

优先从当前仓库根读取 `.agents/skill-adapters/module-analysis.md`，按任务需要使用以下章节：

- `适用仓库`
- `模块路由`
- `架构文档`
- `局部规则与契约`
- `验证`

只使用仓库标识和引用可验证的 adapter 内容。缺失、不完整、仓库不匹配或引用失效时，依据
当前仓库规则、目标代码、调用方和直接证据继续只读分析；标明未知事实，只暂停依赖它们的动作。

## Workflow

1. 通过有效 adapter 或仓库自身路由定位目标模块，读取最近的 local rules；仅选读本次分析需要的文档。
2. 追踪 public entrypoints、upstream callers、downstream dependencies、persisted boundaries，以及
   dynamic 或 framework entrypoints。
3. 识别模块拥有什么、相邻层不能推入什么，以及哪些 invariants 必须在重构后继续成立。
4. 记录理解 main flow 所需的最小 active-code files，以及风险最高的 ownership 或兼容边界。
5. 与当前 module、contract 和 flow docs 交叉核对。
6. 职责、依赖、不变量或风险变化时刷新已有 durable owner，不创建平行模块说明。
7. 依据有效 adapter 或仓库实际入口执行与本次范围相称的验证，总结职责、external contract、
   边界和主要 refactor risk；没有可用验证入口时记录未验证范围，不阻断已有证据支持的分析。
