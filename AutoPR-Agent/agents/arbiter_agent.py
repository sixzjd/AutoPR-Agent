"""裁决 Agent — 汇总子 Agent 结果，生成最终 Review"""

from core.agent_base import BaseAgent, AgentInput, AgentOutput
from core.agent_base import AgentOutput as SubAgentOutput


class ArbiterAgent(BaseAgent):
    """裁决 Agent，负责聚合多个子 Agent 的结果"""

    SYSTEM_PROMPT = """你是一个代码审查裁决专家。你的职责是：
1. 合并多个审查 Agent 的输出结果
2. 去重：多条 Agent 可能报告同一个问题
3. 按严重程度排序：BLOCKER > CRITICAL > WARNING > INFO
4. 生成结构化的最终 Review 结论

输出格式：
```
## Review 总结
[整体评估]

### BLOCKER（必须修复）
- [问题描述] — [位置] — [Agent 来源]

### CRITICAL（建议修复）
...

### WARNING（值得注意）
...

### INFO（仅供参考）
...
```
"""

    async def run(self, inputs: AgentInput) -> AgentOutput:
        # 此方法在 Orchestrator 中会被特殊调用，传入子 Agent 结果
        return AgentOutput(agent_name=self.name, summary="裁决 Agent 就绪")

    async def arbitrate(
        self, spec: SubAgentOutput, change: SubAgentOutput, test: SubAgentOutput
    ) -> AgentOutput:
        """汇总三个子 Agent 的结果，生成最终裁决"""

        reports = f"""
=== 规范 Agent ===
{spec.summary}
{spec.findings}

=== 变更分析 Agent ===
{change.summary}
{change.findings}

=== 测试 Agent ===
{test.summary}
{test.findings}
"""

        result = await self._call_llm(self.SYSTEM_PROMPT, reports)
        return AgentOutput(
            agent_name=self.name,
            summary="Review 裁决完成",
            findings=[{"source": "arbiter", "raw": result}],
        )
