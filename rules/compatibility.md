## 兼容与迁移

- Active compatibility logic 应留在相关实现附近，并说明 why、canonical replacement、
  remove condition 和 durable reference；具体标记格式由仓库规则定义。
- Legacy 接受、fallback、alias 和迁移逻辑应集中在明确兼容分支，不污染 canonical path，也不
  静默改变信任或安全边界。
- 删除 compatibility shim 前检查真实历史生产者、持久化产物、外部调用方、测试和文档；没有
  可验证退出条件时保持兼容或明确 defer。
- 测试保护仍受支持的兼容行为，不新增只证明旧名称、旧文件或旧源码文本已经消失的测试。
