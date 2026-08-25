## 验证与完成

- 优先修改既有 owning tests 和 durable docs；不为 helper 实现细节新增低价值测试或平行文档。
- 运行与风险和 touched ownership 相称的最小检查；局部检查不得描述成全仓库通过，无法运行的
  检查必须说明原因。
- 当 owning acceptance 已有与风险相称的证据，且本次变更没有继续产生直接 orphan、stale
  reference 或未验证 contract 时，停止重复搜索、测试和 review；不新增只用于再次确认完成状态的
  审计循环。
- 区分修改前已有失败和本次新增失败；没有基线证据时不要猜测归因。
- behavior、ownership、contract、artifact、default 或 workflow semantics 变化时更新真实长期
  owner；现有文档仍准确时明确说明无需更新。
- 完成修改时报告 behavior change、public/protected surface、tests、durable docs、保留结构和
  deferred risks。结构精简还应报告任务规则要求的前后阅读成本指标。
