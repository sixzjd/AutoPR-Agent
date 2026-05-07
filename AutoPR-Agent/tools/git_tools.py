"""Git 仓库工具集"""

import subprocess
import tempfile
from pathlib import Path


class GitTools:
    """封装 git diff、日志、文件变更等操作"""

    def __init__(self, repo_path: str | None = None):
        self.repo_path = repo_path
        self._clone_dir: Path | None = None

    async def clone(self, repo_url: str, branch: str) -> str:
        """克隆指定分支到临时目录"""
        self._clone_dir = Path(tempfile.mkdtemp(prefix="autopr_"))
        subprocess.run(
            ["git", "clone", "--depth=1", "-b", branch, repo_url, str(self._clone_dir)],
            check=True, capture_output=True,
        )
        return str(self._clone_dir)

    async def get_diff(self, base: str, head: str) -> str:
        """获取两个分支间的 diff"""
        result = subprocess.run(
            ["git", "diff", f"origin/{base}...origin/{head}", "--", "."],
            cwd=self._clone_dir, capture_output=True, text=True,
        )
        return result.stdout[:50000]  # 限制最大 5 万字符

    async def get_changed_files(self, base: str, head: str) -> list[str]:
        """获取变更文件列表"""
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base}...origin/{head}", "--", "."],
            cwd=self._clone_dir, capture_output=True, text=True,
        )
        return [f for f in result.stdout.splitlines() if f]

    def cleanup(self):
        """清理克隆的仓库"""
        import shutil
        if self._clone_dir and self._clone_dir.exists():
            shutil.rmtree(self._clone_dir, ignore_errors=True)
