#!/bin/bash
# GitHub认证和推送脚本
# 解决HTTPS认证问题

set -e

COMPANY_DIR="$HOME/.openclaw/workspace/company_system"
GITHUB_USER="maoshuorz"
REPO_NAME="nexus-ai"

echo "========================================"
echo "🔐 GitHub认证设置"
echo "========================================"
echo ""

# 方法1: 检查是否已有SSH密钥
setup_ssh() {
    echo "📍 方法1: SSH密钥认证 (推荐)"
    echo ""
    
    if [ -f "$HOME/.ssh/id_rsa.pub" ] || [ -f "$HOME/.ssh/id_ed25519.pub" ]; then
        echo "✅ 检测到已有SSH密钥"
        cat "$HOME/.ssh/id_"*.pub 2>/dev/null | head -1
        echo ""
        echo "请确保已将SSH密钥添加到GitHub:"
        echo "https://github.com/settings/keys"
        echo ""
        
        cd "$COMPANY_DIR"
        git remote set-url origin "git@github.com:$GITHUB_USER/$REPO_NAME.git"
        echo "✅ 已切换为SSH连接"
        echo ""
        echo "执行推送:"
        echo "  git push -u origin main"
    else
        echo "🆕 生成新的SSH密钥..."
        ssh-keygen -t ed25519 -C "nexus-ai@company.com" -f "$HOME/.ssh/id_ed25519" -N ""
        echo ""
        echo "✅ SSH密钥已生成"
        echo ""
        echo "📋 公钥内容:"
        cat "$HOME/.ssh/id_ed25519.pub"
        echo ""
        echo "⚠️  请复制上面的公钥，添加到GitHub:"
        echo "https://github.com/settings/keys"
        echo ""
        echo "添加后，执行:"
        echo "  cd ~/.openclaw/workspace/company_system"
        echo "  git remote set-url origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
        echo "  git push -u origin main"
    fi
}

# 方法2: 使用GitHub CLI
setup_gh() {
    echo "📍 方法2: GitHub CLI (最简单)"
    echo ""
    
    if ! command -v gh &> /dev/null; then
        echo "安装GitHub CLI..."
        brew install gh
    fi
    
    echo "🔑 登录GitHub..."
    gh auth login
    
    echo ""
    echo "✅ 登录成功后，执行推送:"
    echo "  cd ~/.openclaw/workspace/company_system"
    echo "  git push -u origin main"
}

# 方法3: 使用个人访问令牌 (PAT)
setup_pat() {
    echo "📍 方法3: 个人访问令牌 (PAT)"
    echo ""
    echo "1. 访问 https://github.com/settings/tokens"
    echo "2. 点击 'Generate new token (classic)'"
    echo "3. 选择权限: repo (全选)"
    echo "4. 生成并复制令牌"
    echo ""
    echo "5. 然后执行:"
    echo "   cd ~/.openclaw/workspace/company_system"
    echo "   git remote set-url origin https://TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "   (将TOKEN替换为你的实际令牌)"
    echo ""
    echo "6. 推送:"
    echo "   git push -u origin main"
}

# 显示菜单
echo "选择认证方式:"
echo ""
echo "1) SSH密钥 (最安全，推荐)"
echo "2) GitHub CLI (最简单)"
echo "3) 个人访问令牌 (PAT)"
echo ""
read -p "请输入选项 (1-3): " choice

case $choice in
    1)
        setup_ssh
        ;;
    2)
        setup_gh
        ;;
    3)
        setup_pat
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
