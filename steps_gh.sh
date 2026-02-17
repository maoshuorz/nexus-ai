#!/bin/bash
# GitHub CLI 安装和登录 - 完整步骤

echo "========================================"
echo "🚀 GitHub CLI 完整安装流程"
echo "========================================"
echo ""

# 步骤1: 检查Homebrew
if command -v brew &> /dev/null; then
    echo "✅ Homebrew已安装"
    echo ""
    echo "执行安装命令:"
    echo "  brew install gh"
    echo ""
else
    echo "⚠️  需要安装Homebrew"
    echo ""
    echo "安装Homebrew:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    echo "安装完成后，运行:"
    echo "  brew install gh"
fi

echo "========================================"
echo ""
echo "步骤2: 登录GitHub"
echo "  gh auth login"
echo ""
echo "按提示选择:"
echo "  ✓ GitHub.com"
echo "  ✓ HTTPS"
echo "  ✓ Yes (使用GitHub凭证)"
echo "  ✓ Login with a web browser"
echo ""
echo "========================================"
echo ""
echo "步骤3: 配置Git"
echo "  gh auth setup-git"
echo ""
echo "========================================"
echo ""
echo "步骤4: 推送代码"
echo "  cd ~/.openclaw/workspace/company_system"
echo "  git push -u origin main"
echo ""
echo "========================================"
echo "✅ 完成！网站地址:"
echo "   https://maoshuorz.github.io/nexus-ai/"
echo "========================================"
