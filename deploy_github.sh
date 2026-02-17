#!/bin/bash
# Nexus AI 一键部署脚本 - GitHub Pages
# 用户: maoshuorz

set -e

REPO_NAME="nexus-ai"
GITHUB_USER="maoshuorz"
COMPANY_DIR="$HOME/.openclaw/workspace/company_system"

echo "========================================"
echo "🚀 Nexus AI GitHub Pages 部署脚本"
echo "========================================"
echo ""
echo "GitHub用户: $GITHUB_USER"
echo "仓库名称: $REPO_NAME"
echo ""

# 检查GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "📦 安装GitHub CLI..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    else
        echo "请手动安装GitHub CLI: https://cli.github.com/"
        exit 1
    fi
fi

# 登录GitHub
echo ""
echo "🔑 检查GitHub登录状态..."
if ! gh auth status &> /dev/null; then
    echo "请先登录GitHub:"
    gh auth login
fi

# 创建GitHub仓库
echo ""
echo "📁 创建GitHub仓库..."
cd "$COMPANY_DIR"

if gh repo view "$GITHUB_USER/$REPO_NAME" &> /dev/null; then
    echo "✅ 仓库已存在"
else
    echo "🆕 创建新仓库..."
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    echo "✅ 仓库创建成功"
fi

# 设置远程仓库
echo ""
echo "🔗 配置远程仓库..."
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || \
git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

# 推送代码
echo ""
echo "📤 推送代码到GitHub..."
git push -u origin main

# 启用GitHub Pages
echo ""
echo "🌐 启用GitHub Pages..."
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/$GITHUB_USER/$REPO_NAME/pages \
  -f source='{"branch":"main","path":"/"}'

# 等待部署
echo ""
echo "⏳ 等待GitHub Pages部署..."
sleep 10

# 获取网站地址
echo ""
echo "========================================"
echo "🎉 部署成功！"
echo "========================================"
echo ""
echo "🌐 网站地址:"
echo "   https://$GITHUB_USER.github.io/$REPO_NAME/"
echo ""
echo "📊 监控页面:"
echo "   https://$GITHUB_USER.github.io/$REPO_NAME/stage_monitor_v2.html"
echo ""
echo "📁 GitHub仓库:"
echo "   https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "⚠️ 注意: GitHub Pages首次部署可能需要5-10分钟生效"
echo ""
