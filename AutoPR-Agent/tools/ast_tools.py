"""AST 解析与依赖分析工具"""

import ast
import re
from pathlib import Path


class ASTRuleChecker:
    """基于 AST 的代码规范检查"""

    FORBIDDEN_IMPORTS = {
        "java": {"import sun.*": "禁止使用 sun 内部 API"},
        "go": {"log.Println": "请使用结构化日志库"},
    }

    LAYER_RULES = {
        "controller": {"allowed_deps": ["service", "dto"], "forbidden_deps": ["dao", "repository"]},
        "service": {"allowed_deps": ["dao", "repository", "client"], "forbidden_deps": ["controller"]},
    }

    def check_imports(self, file_path: str, lang: str) -> list[dict]:
        """检查文件导入是否违反规范"""
        findings = []
        content = Path(file_path).read_text() if Path(file_path).exists() else ""

        if lang == "python":
            return self._check_python_imports(content, file_path)
        return findings

    def _check_python_imports(self, content: str, file_path: str) -> list[dict]:
        findings = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("tests.") and "src" in file_path:
                            findings.append({
                                "file": file_path,
                                "line": node.lineno,
                                "rule": "IMPORT-001",
                                "severity": "error",
                                "message": f"生产代码不应引入测试模块: {alias.name}",
                            })
        except SyntaxError:
            pass
        return findings

    def get_dependency_graph(self, files: list[str]) -> dict[str, set[str]]:
        """构建文件间的依赖关系图"""
        graph: dict[str, set[str]] = {}
        import_pattern = re.compile(r'^import\s+["\'](.+?)["\']', re.MULTILINE)
        for file in files:
            try:
                content = Path(file).read_text()
                deps = set(import_pattern.findall(content))
                graph[file] = deps
            except Exception:
                continue
        return graph
