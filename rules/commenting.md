## 注释与文档表达

- 注释和 docstring 解释职责、不变量、数据 shape、设计原因、副作用、失败边界和非显然取舍，
  不逐行复述实现，也不为补注释改变行为。
- 修改复杂逻辑时检查整个 touched region 的既有说明，更新或删除失真注释。
- 不给 trivial getter、passthrough 或显然赋值增加冗长说明；错误 ownership 应通过代码结构解决，
  不用注释掩盖。
- 默认用简体中文编写说明性 Markdown、注释和 docstring；路径、标识符、命令、配置键、日志和
  代码保持原文。用户或更具体仓库规则明确要求其它语言时服从更具体要求。
- 长期文档描述当前生效事实；历史背景只进入 ADR、migration、audit、review 或兼容说明。
