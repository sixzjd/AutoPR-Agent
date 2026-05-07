"""
AutoPR · 多 Agent 协作的代码质量保障系统

使用方式:
  # 审查一个 PR
  python main.py --pr-url https://github.com/org/repo/pull/42

  # 启动 Webhook 服务
  python main.py --server --port 8080

  # 分析本地 diff
  python main.py --diff-file /path/to/diff.txt
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import yaml

# 将项目根目录加入 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from anthropic import AsyncAnthropic
from core.agent_base import AgentInput
from core.orchestrator import Orchestrator
from agents.spec_agent import SpecAgent
from agents.change_analysis_agent import ChangeAnalysisAgent
from agents.test_agent import TestAgent
from agents.arbiter_agent import ArbiterAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("autopr")


def load_config() -> dict:
    """加载配置"""
    config_path = Path(__file__).parent / "config" / "settings.yaml"
    if not config_path.exists():
        logger.warning("配置文件不存在，使用默认配置")
        return {}

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # 环境变量覆盖
    if os.getenv("GITHUB_TOKEN"):
        config.setdefault("github", {})["token"] = os.getenv("GITHUB_TOKEN")
    if os.getenv("ANTHROPIC_API_KEY"):
        config.setdefault("anthropic", {})["api_key"] = os.getenv("ANTHROPIC_API_KEY")

    return config


def create_orchestrator(config: dict) -> Orchestrator:
    """初始化 Agent 和编排器"""
    anthropic_config = config.get("anthropic", {})
    client = AsyncAnthropic(api_key=anthropic_config.get("api_key"))

    spec_agent = SpecAgent(
        name="spec-agent",
        model=anthropic_config.get("models", {}).get("spec_agent", "claude-sonnet-4-20250514"),
        client=client,
    )
    change_agent = ChangeAnalysisAgent(
        name="change-analysis-agent",
        model=anthropic_config.get("models", {}).get("change_agent", "claude-opus-4-20250514"),
        client=client,
    )
    test_agent = TestAgent(
        name="test-agent",
        model=anthropic_config.get("models", {}).get("test_agent", "claude-sonnet-4-20250514"),
        client=client,
    )
    arbiter = ArbiterAgent(
        name="arbiter",
        model=anthropic_config.get("models", {}).get("arbiter", "claude-opus-4-20250514"),
        client=client,
    )

    return Orchestrator(
        spec_agent=spec_agent,
        change_agent=change_agent,
        test_agent=test_agent,
        arbiter=arbiter,
    )


async def review_pr(orchestrator: Orchestrator, pr_url: str):
    """审查指定 PR"""
    # 解析 PR URL: https://github.com/{owner}/{repo}/pull/{number}
    parts = pr_url.rstrip("/").split("/")
    pr_number = int(parts[-1])
    repo_name = "/".join(parts[-4:-2])

    logger.info("开始审查 %s #%d", repo_name, pr_number)

    # 构造 AgentInput（实际使用时会通过 GitTools 获取 diff）
    inputs = AgentInput(
        pr_number=pr_number,
        repo_name=repo_name,
        diff="示例 diff 内容 — 实际使用时会从 GitHub API 获取",
        changed_files=["src/main/java/com/example/OrderService.java"],
        branch="feature/add-payment",
        base_branch="main",
    )

    result = await orchestrator.review(inputs)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


async def start_webhook_server(orchestrator: Orchestrator, port: int):
    """启动 GitHub Webhook 服务"""
    try:
        from httpx import AsyncClient
        from http.server import HTTPServer, BaseHTTPRequestHandler
    except ImportError:
        logger.error("需要安装 httpx: pip install httpx")
        return

    logger.info("Webhook 服务启动在 :%d", port)
    # 实际项目中使用 FastAPI / Flask
    # 此处为示意图
    print(f"Server would start on port {port}")


async def review_local_diff(orchestrator: Orchestrator, diff_path: str):
    """审查本地 diff 文件"""
    diff_content = Path(diff_path).read_text(encoding="utf-8")
    inputs = AgentInput(
        pr_number=0,
        repo_name="local",
        diff=diff_content[:50000],
        changed_files=["local/file"],
        branch="local",
        base_branch="main",
    )
    result = await orchestrator.review(inputs)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main():
    parser = argparse.ArgumentParser(description="AutoPR — 多 Agent 代码审查系统")
    parser.add_argument("--pr-url", help="GitHub PR URL")
    parser.add_argument("--server", action="store_true", help="启动 Webhook 服务")
    parser.add_argument("--port", type=int, default=8080, help="Webhook 端口")
    parser.add_argument("--diff-file", help="审查本地 diff 文件")
    parser.add_argument("--config", default="config/settings.yaml", help="配置文件路径")

    args = parser.parse_args()
    config = load_config()
    orchestrator = create_orchestrator(config)

    if args.pr_url:
        asyncio.run(review_pr(orchestrator, args.pr_url))
    elif args.server:
        asyncio.run(start_webhook_server(orchestrator, args.port))
    elif args.diff_file:
        asyncio.run(review_local_diff(orchestrator, args.diff_file))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
