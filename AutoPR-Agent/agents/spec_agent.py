"""规范 Agent — 检查 PR 代码是否符合团队架构规范"""

from core.agent_base import BaseAgent, AgentInput, AgentOutput


class SpecAgent(BaseAgent):
    """架构规范检查 Agent"""

    SYSTEM_PROMPT = """你是一个代码规范审查专家。你的职责是：
1. 检查代码是否违反团队架构规范（分层依赖、命名约定、异常处理）
2. 基于 diff 逐文件审查
3. 按严重级别输出：BLOCKER / CRITICAL / WARNING / INFO

规范规则（部分示例）：
- Controller 层不能直接依赖 DAO/Repository
- Service 层不能依赖其他 Service 的具体实现，应依赖接口
- 所有外部 API 调用必须包含超时和重试
- 禁止使用 System.out.println / print (应使用结构化日志)
- 方法超过 100 行需要拆分
"""

    async def run(self, inputs: AgentInput) -> AgentOutput:
        prompt = f"""请审查以下 PR #{
            inputs.pr_number} 的代码变更 ({inputs.repo_name})。

变更分支: {inputs.branch} → {inputs.base_branch}
变更文件: {', '.join(inputs.changed_files[:20])}

Diff:
```diff
{inputs.diff[:30000]}
```

请列出所有规范违规，按严重程度排序输出 JSON 格式。"""

        result = await self._call_llm(self.SYSTEM_PROMPT, prompt)
        return AgentOutput(
            agent_name=self.name,
            summary=f"规范检查完成，发现违规项（详见 findings）",
            findings=[{"source": "spec_agent", "raw": result}],
        )
