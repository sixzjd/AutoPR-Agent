"""测试 Agent — 分析测试覆盖，生成测试建议"""

from core.agent_base import BaseAgent, AgentInput, AgentOutput


class TestAgent(BaseAgent):
    """测试覆盖分析 Agent"""

    SYSTEM_PROMPT = """你是一个测试分析专家。你的职责是：
1. 分析新增代码是否被现有测试覆盖
2. 识别未覆盖的分支和边界条件
3. 生成具体的测试用例建议（包括正常路径和异常路径）
4. 检查测试代码本身的质量

输出的测试建议应包含：
- 被测方法 / 函数
- 建议的测试场景
- 输入 / 期望输出
- 优先级
"""

    async def run(self, inputs: AgentInput) -> AgentOutput:
        prompt = f"""请分析以下 PR 的测试覆盖情况。

PR #{inputs.pr_number} ({inputs.repo_name})
变更文件: {len(inputs.changed_files)} 个

Diff:
```diff
{inputs.diff[:30000]}
```

请分析：
1. 哪些新增代码缺少测试覆盖？
2. 建议补充哪些测试用例？
3. 现有测试是否需要更新？"""

        result = await self._call_llm(self.SYSTEM_PROMPT, prompt)
        return AgentOutput(
            agent_name=self.name,
            summary="测试覆盖分析完成",
            findings=[{"source": "test_agent", "raw": result}],
        )
