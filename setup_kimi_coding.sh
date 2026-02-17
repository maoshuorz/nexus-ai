#!/bin/bash
# Kimi Coding 配置脚本
# 配置Anthropic兼容模式的Kimi Coding API

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Kimi Coding 配置助手                                     ║"
echo "║     Anthropic API 兼容模式                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 提示用户输入API Key
echo "🔑 请输入你的 Kimi Coding API Key:"
echo "   (从 https://kimi.com 会员页面获取)"
read -s API_KEY

echo ""
echo "✅ API Key已接收"
echo ""

# 设置环境变量
export ANTHROPIC_API_KEY="$API_KEY"
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding"
export KIMI_MODEL="kimi-coding/k2p5"

echo "📝 当前配置:"
echo "   ANTHROPIC_API_KEY: ${API_KEY:0:20}..."
echo "   ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL"
echo "   KIMI_MODEL: $KIMI_MODEL"
echo ""

# 测试连接
echo "🔍 测试API连接..."
cd "$(dirname "$0")"
python3 kim_coding_runner.py

echo ""
echo "💡 永久配置（添加到 ~/.zshrc）:"
echo ""
echo "export ANTHROPIC_API_KEY='${API_KEY}'"
echo "export ANTHROPIC_BASE_URL='https://api.kimi.com/coding'"
echo "export KIMI_MODEL='kimi-coding/k2p5'"
echo ""

echo "运行以下命令添加到配置文件:"
echo "   echo 'export ANTHROPIC_API_KEY=\"${API_KEY}\"' >> ~/.zshrc"
echo "   echo 'export ANTHROPIC_BASE_URL=\"https://api.kimi.com/coding\"' >> ~/.zshrc"
echo "   echo 'export KIMI_MODEL=\"kimi-coding/k2p5\"' >> ~/.zshrc"
