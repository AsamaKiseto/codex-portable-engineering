---
name: knowledge-sync
description: 把 behavior、ownership、contract、artifact、default 和 workflow 变化同步到仓库长期文档 owner。代码或规则改变长期工程事实，或文档 ownership 可能漂移时使用。
---

# 知识同步

把变化映射到既有 durable knowledge owner，避免重复文档。

## Repository adapter gate

优先从当前仓库根读取 `.agents/skill-adapters/knowledge-sync.md`，按任务需要使用以下章节：

- `适用仓库`
- `变更路由`
- `长期文档 owner`
- `模板与格式`
- `验证`

只使用仓库标识、路由及 owner 可验证的 adapter 内容。缺失或无效时依据仓库规则与直接证据
定位 owner；在已有修改授权内更新能确认的事实。owner 仍不明确时仅暂停对应写入，继续其余核对。

## Workflow

1. 判断哪些 changed paths 和行为具有长期语义。
2. 使用有效 adapter 或仓库自身路由，按本任务 changed paths 选读相关 local rules、tests 和
   文档；不把无关的已有 diff 纳入本任务验收。
3. 按 ownership 分类 durable change：architecture 记录职责、依赖和分层；contract 记录字段、
   行为、默认值、不变量和失败语义；flow 记录生命周期、顺序、分支和副作用；decision record
   记录长期选择和 tradeoff。
4. 既有 owner 能清楚承载事实时直接更新；只有所有现有 owner 都会混淆职责时才新建文档。
5. 记录稳定事实，不写聊天历史、临时排障细节或重复 policy。
6. 使用有效 adapter 或仓库文档中可确认的模板、语言和兼容约定。
7. 运行与本次范围相称的仓库验证，报告更新的 owner；无需更新时说明现有文档为何仍然正确。
