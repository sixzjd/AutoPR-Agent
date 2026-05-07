# AutoPR · 多 Agent 协作的代码质量保障系统

基于多 Agent 协作的自动化代码审查系统，将人工 Review 聚焦在架构设计和业务逻辑上，把模式化审查自动化。

## 架构

```
[GitHub Webhook] → [PR Event Bus]
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       [规范 Agent]  [变更分析 Agent]  [测试 Agent]
            │            │            │
            └────────────┼────────────┘
                         ▼
                    [裁决 Agent]
                         │
                   [PR Comment] + [Label]
```

## Agent 职责

| Agent | 职责 | 模型 |
|-------|------|------|
| 规范 Agent | 检查架构规范合规性 | Claude Sonnet |
| 变更分析 Agent | 分析 PR 影响面与风险 | Claude Opus |
| 测试 Agent | 测试覆盖分析与建议 | Claude Sonnet |
| 裁决 Agent | 聚合结果、排序优先级 | Claude Opus |

## 快速开始

```bash
pip install -r requirements.txt
cp config/settings.example.yaml config/settings.yaml
# 编辑 settings.yaml 填入 GitHub Token 和 API Key
python main.py --pr-url https://github.com/org/repo/pull/42
```
