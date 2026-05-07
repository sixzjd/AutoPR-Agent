"""变更分析 Agent — 理解 PR 语义变更，检测影响面"""

from core.agent_base import BaseAgent, AgentInput, AgentOutput


class ChangeAnalysisAgent(BaseAgent):
    """变更影响分析 Agent"""

    SYSTEM_PROMPT = """你是一个系统变更影响分析专家。你的职责是：
1. 理解 PR 的语义变更（不仅仅是语法层面）
2. 判断变更是否触及核心领域模型或关键链路
3. 评估影响面：哪些模块需要回归测试
4. 识别循环依赖、破坏性 API 变更等风险

输出格式：
- impact: high / medium / low
- affected_modules: 受影响模块列表
- risks: 风险项列表
"""

    async def run(self, inputs: AgentInput) -> AgentOutput:
        prompt = f"""请分析以下 PR 变更的影响范围。

PR #{inputs.pr_number} ({inputs.repo_name})
分支: {inputs.branch} → {inputs.base_branch}

变更文件 ({len(inputs.changed_files)} 个):
{chr(10).join(f'  - {f}' for f in inputs.changed_files[:30])}

Diff:
```diff
{inputs.diff[:30000]}
```

请分析变更的影响范围、风险等级，推荐需要回归测试的模块。"""

        result = await self._call_llm(self.SYSTEM_PROMPT, prompt)
        return AgentOutput(
            agent_name=self.name,
            summary="变更影响分析完成",
            findings=[{"source": "change_analysis", "raw": result}],
        )
