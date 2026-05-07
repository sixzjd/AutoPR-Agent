"""Agent 基类 — 所有 Agent 的通用抽象"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentInput:
    pr_number: int
    repo_name: str
    diff: str
    changed_files: list[str]
    branch: str
    base_branch: str


@dataclass
class AgentOutput:
    agent_name: str
    findings: list[dict] = field(default_factory=list)
    summary: str = ""
    error: str | None = None


class BaseAgent(ABC):
    """Agent 基类，所有子 Agent 继承此接口"""

    def __init__(self, name: str, model: str, client: Any):
        self.name = name
        self.model = model
        self.client = client
        self.timeout = 30

    @abstractmethod
    async def run(self, inputs: AgentInput) -> AgentOutput:
        """执行 Agent 的核心逻辑"""
        ...

    async def _call_llm(self, system: str, prompt: str) -> str:
        """统一的 LLM 调用封装，含重试和超时"""
        import asyncio

        for attempt in range(2):
            try:
                resp = await asyncio.wait_for(
                    self.client.messages.create(
                        model=self.model,
                        max_tokens=4096,
                        system=system,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                    timeout=self.timeout,
                )
                return resp.content[0].text
            except asyncio.TimeoutError:
                if attempt == 1:
                    return "【Agent 超时】任务未完成"
                continue
            except Exception as e:
                if attempt == 1:
                    return f"【Agent 错误】{e}"
                continue
        return "【Agent 失败】"
