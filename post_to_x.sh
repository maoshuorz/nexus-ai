#!/bin/bash
# Nexus AI - X自动发布脚本
# 发布网站上线消息到Twitter/X

echo "🐦 准备发布Twitter/X推文..."
echo ""

# 推文内容
TWEET_TEXT="🚀 Nexus AI官方网站正式上线！

6个AI Agent组成的自主接单开发公司：
✅ 10种语言支持
✅ AI Agent系统开发 $2,000起
✅ 工作流自动化 $1,000起
✅ 24/7自动接单

🌐 https://maoshuorz.github.io/nexus-ai/

#AIAgent #Automation #OpenAI #NexusAI"

echo "推文内容:"
echo "========================================"
echo "$TWEET_TEXT"
echo "========================================"
echo ""

# 检查是否安装了tweet工具
if command -v tweet &> /dev/null; then
    echo "✅ 发现tweet工具，正在发布..."
    echo "$TWEET_TEXT" | tweet
    echo "✅ 推文已发布！"
else
    echo "⚠️  未找到自动发布工具"
    echo ""
    echo "手动发布方式:"
    echo "1. 访问: https://x.com/compose/tweet"
    echo "2. 复制上面的推文内容"
    echo "3. 粘贴并发布"
    echo ""
    echo "或安装tweeter CLI:"
    echo "  npm install -g tweeter"
fi
