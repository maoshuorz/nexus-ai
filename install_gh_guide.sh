#!/bin/bash
# GitHub CLI 手动安装和登录指南
# 方案1: GitHub CLI认证

echo "========================================"
echo "🔧 GitHub CLI 安装指南"
echo "========================================"
echo ""

# 检测系统类型
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        PKG="gh_${VERSION}_macOS_arm64.zip"
    else
        PKG="gh_${VERSION}_macOS_amd64.zip"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    OS="Unknown"
fi

echo "📱 检测到系统: $OS"
echo ""

# 下载链接
VERSION="2.40.1"
echo "📦 GitHub CLI版本: $VERSION"
echo ""

# macOS安装方式
if [ "$OS" = "macOS" ]; then
    echo "🍎 macOS安装方式:"
    echo ""
    echo "方式A - 使用Homebrew (推荐):"
    echo "  打开终端，运行:"
    echo "    brew install gh"
    echo ""
    echo "方式B - 手动下载:"
    echo "  1. 下载: https://github.com/cli/cli/releases/download/v${VERSION}/gh_${VERSION}_macOS_universal.pkg"
    echo "  2. 双击安装包安装"
    echo ""
fi

# Linux安装方式
if [ "$OS" = "Linux" ]; then
    echo "🐧 Linux安装方式:"
    echo ""
    echo "方式A - 使用包管理器:"
    echo "  Debian/Ubuntu:"
    echo "    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null"
    echo "    sudo apt update"
    echo "    sudo apt install gh"
    echo ""
    echo "方式B - 手动下载:"
    echo "  https://github.com/cli/cli/releases/latest"
    echo ""
fi

echo "========================================"
echo "🔐 安装完成后，执行以下步骤:"
echo "========================================"
echo ""
echo "步骤1: 验证安装"
echo "  gh --version"
echo ""
echo "步骤2: 登录GitHub"
echo "  gh auth login"
echo ""
echo "  选择:"
echo "    - What account do you want to log into? → GitHub.com"
echo "    - What is your preferred protocol for Git operations? → HTTPS"
echo "    - Authenticate Git with your GitHub credentials? → Yes"
echo "    - How would you like to authenticate? → Login with a web browser"
echo ""
echo "步骤3: 配置git使用GitHub CLI"
echo "  gh auth setup-git"
echo ""
echo "步骤4: 推送代码"
echo "  cd ~/.openclaw/workspace/company_system"
echo "  git push -u origin main"
echo ""
echo "========================================"
echo "✅ 完成后，网站将部署到:"
echo "   https://maoshuorz.github.io/nexus-ai/"
echo "========================================"
