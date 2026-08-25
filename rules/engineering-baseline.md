## 通用工程基线

- 除非任务明确要求改变，否则保持已有行为、外部契约和持久化格式。
- 修改前检查完整 working tree，保留用户已有和无关修改，不回退、不覆盖、不顺手清理。
- 可读性和真实 ownership 优先于机械减少行数、函数数或文件数；不使用更深嵌套、新 thin
  wrapper、透传 adapter、重复 schema 或 speculative abstraction 制造表面精简。
- 删除、重命名、移动或削弱 public API、CLI、callback、registry/discovery、serialization、
  migration、operational script 或已文档化 contract 前，检查静态引用、动态入口、测试和文档，
  并明确兼容与迁移边界。
- 低引用计数、文件短或实现简单本身不足以改变 protected surface；协议、类型收窄、资源边界和
  side-effect isolation 具有独立价值。
