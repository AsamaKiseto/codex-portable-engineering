---
name: knowledge-sync
description: 把 behavior、ownership、contract、artifact、default 和 workflow 变化同步到仓库长期文档 owner。代码或规则改变长期工程事实，或文档 ownership 可能漂移时使用。
---

# 知识同步

把变化映射到既有 durable knowledge owner，避免重复文档。

## Repository adapter gate

执行前从当前仓库根读取 `.agents/skill-adapters/knowledge-sync.md`，并要求以下章节非空：

- `适用仓库`
- `变更路由`
- `长期文档 owner`
- `模板与格式`
- `验证`

adapter 必须给出可验证的仓库标识、change-to-document 路由和真实验证入口。adapter 缺失、
不完整、仓库不匹配或引用不存在的 owner 时停止。

## Workflow

1. 判断哪些 changed paths 和行为具有长期语义。
2. 使用 adapter 的路由源定位最近的 local rules、tests、architecture docs、contracts、flows
   和 decision records。
3. 按 ownership 分类 durable change：architecture 记录职责、依赖和分层；contract 记录字段、
   行为、默认值、不变量和失败语义；flow 记录生命周期、顺序、分支和副作用；decision record
   记录长期选择和 tradeoff。
4. 既有 owner 能清楚承载事实时直接更新；只有所有现有 owner 都会混淆职责时才新建文档。
5. 记录稳定事实，不写聊天历史、临时排障细节或重复 policy。
6. 使用 adapter 指定的模板、语言和兼容约定。
7. 运行仓库验证，报告更新的 owner；无需更新时说明现有文档为何仍然正确。
