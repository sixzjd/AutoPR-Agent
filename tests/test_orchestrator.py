"""Orchestrator 单元测试"""

import pytest
from core.agent_base import AgentInput, AgentOutput
from core.orchestrator import Orchestrator


class MockAgent:
    def __init__(self, name: str):
        self.name = name

    async def run(self, inputs: AgentInput) -> AgentOutput:
        return AgentOutput(agent_name=self.name, summary=f"{self.name} done")

    async def arbitrate(self, *args, **kwargs):
        return AgentOutput(agent_name="arbiter", summary="All done")


@pytest.mark.asyncio
async def test_orchestrator_parallel_execution():
    """测试三个子 Agent 是否并行执行"""
    spec = MockAgent("spec")
    change = MockAgent("change")
    test = MockAgent("test")
    arbiter = MockAgent("arbiter")

    orch = Orchestrator(spec, change, test, arbiter)
    inputs = AgentInput(
        pr_number=1, repo_name="test/repo",
        diff="", changed_files=[], branch="feat", base_branch="main",
    )

    result = await orch.review(inputs)
    assert result["pr_number"] == 1
    assert "agents" in result


@pytest.mark.asyncio
async def test_orchestrator_partial_failure():
    """测试单个 Agent 失败不影响整体流程"""
    class FailingAgent(MockAgent):
        async def run(self, inputs):
            raise RuntimeError("mock failure")

    orch = Orchestrator(FailingAgent("spec"), MockAgent("change"), MockAgent("test"), MockAgent("arbiter"))
    inputs = AgentInput(
        pr_number=2, repo_name="test/repo",
        diff="", changed_files=[], branch="feat", base_branch="main",
    )
    result = await orch.review(inputs)
    assert "error" in result["agents"]["spec"]
