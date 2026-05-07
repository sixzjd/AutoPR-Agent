#!/bin/bash
# AutoPR 项目初始化脚本

set -e

echo "🔧 AutoPR 项目初始化..."

# 1. Python 虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
echo "✅ 依赖安装完成"

# 3. 配置检查
if [ ! -f "config/settings.yaml" ]; then
    cp config/settings.yaml config/settings.yaml
    echo "⚠️  请编辑 config/settings.yaml 填入 API Key"
fi

echo ""
echo "✅ AutoPR 初始化完成"
echo "运行: python main.py --pr-url <pr-url>"
