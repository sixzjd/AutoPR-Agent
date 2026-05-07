# 架构规范规则

## 分层依赖 (Layer Rules)

- Controller → Service, DTO
- Service → DAO, Repository, Client
- DAO/Repository → 不允许反向依赖

## 命名规范

- Controller: `XxxController`
- Service 接口: `XxxService` / 实现: `XxxServiceImpl`
- DAO: `XxxDao`
- Repository: `XxxRepository`

## 异常处理

- 所有外部调用必须有 `try-catch` + 超时
- 禁止吞异常（catch 块为空）
- 禁止 `e.printStackTrace()`

## 日志

- 禁止 `System.out.println`
- 必须使用 `slf4j` Logger

## 代码规范

- 方法不超过 100 行
- 类不超过 500 行
- 循环嵌套不超过 3 层
