#!/bin/bash
# ============================================================
# 贡献者成长体系 - 全自动工作流 (总控脚本)
# 用法: ./run.sh
# ============================================================

set -e

echo "🚀 启动贡献者成长体系自动化工作流..."
echo "⏰ 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查 gitlink-cli 是否安装
if ! command -v gitlink-cli &> /dev/null; then
    echo "❌ 错误: gitlink-cli 未安装，请先运行 npm install -g @gitlink-ai/cli"
    exit 1
fi

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python 3 未安装"
    exit 1
fi

# 运行 Python 核心脚本
python3 calculate1.py

# 检查是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 工作流执行成功！"
    echo "📊 报告已生成: output/CONTRIBUTORS.md"
    echo ""
    echo "💡 你可以:"
    echo "   - 查看报告: cat output/CONTRIBUTORS.md"
    echo "   - 自动提交: git add output/CONTRIBUTORS.md && git commit -m '更新排行榜'"
    echo "   - 自动评论: gitlink-cli issue +comment --repo <repo> --id <issue_id> --body \"$(cat output/CONTRIBUTORS.md)\""
else
    echo "❌ 工作流执行失败，请检查错误信息"
    exit 1
fi