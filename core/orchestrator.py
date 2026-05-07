"""Orchestrator — 编排多 Agent 协作流程"""

import asyncio
import logging

from core.agent_base import AgentInput
from agents.spec_agent import SpecAgent
from agents.change_analysis_agent import ChangeAnalysisAgent
from agents.test_agent import TestAgent
from agents.arbiter_agent import ArbiterAgent

logger = logging.getLogger("autopr.orchestrator")


class Orchestrator:
    """多 Agent 协作编排器"""

    def __init__(
        self,
        spec_agent: SpecAgent,
        change_agent: ChangeAnalysisAgent,
        test_agent: TestAgent,
        arbiter: ArbiterAgent,
    ):
        self.spec_agent = spec_agent
        self.change_agent = change_agent
        self.test_agent = test_agent
        self.arbiter = arbiter

    async def review(self, inputs: AgentInput) -> dict:
        """
        执行完整的 PR Review 流程：
        1. 并行执行规范/变更分析/测试三个子 Agent
        2. 裁决 Agent 聚合结果
        3. 返回最终 Review 结论
        """
        logger.info(
            "开始审查 PR #%s (%s), 变更文件: %d",
            inputs.pr_number, inputs.repo_name, len(inputs.changed_files),
        )

        # Step 1: 并行执行三个子 Agent
        spec_task = self.spec_agent.run(inputs)
        change_task = self.change_agent.run(inputs)
        test_task = self.test_agent.run(inputs)

        spec_result, change_result, test_result = await asyncio.gather(
            spec_task, change_task, test_task, return_exceptions=True
        )

        # 处理可能的异常
        for name, result in [("spec", spec_result), ("change", change_result), ("test", test_result)]:
            if isinstance(result, Exception):
                logger.error("%s Agent 执行失败: %s", name, result)

        # Step 2: 裁决 Agent 聚合
        arbiter_result = await self.arbiter.arbitrate(
            spec_result if not isinstance(spec_result, Exception) else None,
            change_result if not isinstance(change_result, Exception) else None,
            test_result if not isinstance(test_result, Exception) else None,
        )

        # Step 3: 计算总体评分
        total_findings = []
        for r in [spec_result, change_result, test_result]:
            if not isinstance(r, Exception) and r:
                total_findings.extend(r.findings)

        result = {
            "pr_number": inputs.pr_number,
            "repo": inputs.repo_name,
            "agents": {
                "spec": self._safe_output(spec_result),
                "change_analysis": self._safe_output(change_result),
                "test": self._safe_output(test_result),
                "arbiter": {
                    "summary": arbiter_result.summary,
                    "findings": arbiter_result.findings,
                },
            },
            "total_findings": len(total_findings),
        }

        logger.info("PR #%s 审查完成，共 %d 项发现", inputs.pr_number, result["total_findings"])
        return result

    def _safe_output(self, result):
        if isinstance(result, Exception):
            return {"error": str(result)}
        return {"summary": result.summary, "findings": result.findings}
