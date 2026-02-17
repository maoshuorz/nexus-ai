#!/bin/bash
# Nexus AI 网站部署脚本
# 自动部署到 GitHub Pages / Vercel / Netlify

set -e

COMPANY_DIR="$HOME/.openclaw/workspace/company_system"
LOG_FILE="$COMPANY_DIR/deploy.log"

echo "========================================"
echo "🚀 Nexus AI 网站部署工具"
echo "========================================"
echo ""

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查文件
check_files() {
    log "检查网站文件..."
    
    if [ ! -f "$COMPANY_DIR/index_v2.html" ]; then
        log "❌ 错误: index_v2.html 不存在"
        exit 1
    fi
    
    if [ ! -f "$COMPANY_DIR/stage_monitor_v2.html" ]; then
        log "❌ 错误: stage_monitor_v2.html 不存在"
        exit 1
    fi
    
    log "✅ 所有文件检查通过"
}

# GitHub Pages 部署
deploy_github() {
    log ""
    log "📦 部署到 GitHub Pages..."
    
    cd "$COMPANY_DIR"
    
    # 检查是否是git仓库
    if [ ! -d ".git" ]; then
        log "初始化Git仓库..."
        git init
        git config user.email "nexus-ai@company.com"
        git config user.name "Nexus AI"
    fi
    
    # 创建或切换到main分支
    git checkout -b main 2>/dev/null || git checkout main
    
    # 添加所有文件
    git add .
    git commit -m "Deploy Nexus AI website - $(date '+%Y-%m-%d %H:%M:%S')" || true
    
    log ""
    log "✅ GitHub Pages 部署准备完成"
    log ""
    log "下一步操作:"
    log "1. 在GitHub创建仓库: https://github.com/new"
    log "2. 复制仓库URL (例如: https://github.com/username/nexus-ai.git)"
    log "3. 运行: git remote add origin YOUR_REPO_URL"
    log "4. 运行: git push -u origin main"
    log "5. 在GitHub仓库Settings -> Pages中启用GitHub Pages"
    log ""
    log "网站将部署到: https://username.github.io/nexus-ai/"
}

# Vercel 部署
deploy_vercel() {
    log ""
    log "📦 部署到 Vercel..."
    
    cd "$COMPANY_DIR"
    
    # 检查是否安装Vercel CLI
    if ! command -v vercel &> /dev/null; then
        log "安装Vercel CLI..."
        npm install -g vercel
    fi
    
    log "启动Vercel部署..."
    vercel --prod
}

# Netlify 部署
deploy_netlify() {
    log ""
    log "📦 部署到 Netlify..."
    
    cd "$COMPANY_DIR"
    
    # 检查是否安装Netlify CLI
    if ! command -v netlify &> /dev/null; then
        log "安装Netlify CLI..."
        npm install -g netlify-cli
    fi
    
    log "启动Netlify部署..."
    netlify deploy --prod --dir=.
}

# 本地预览
preview_local() {
    log ""
    log "🖥️  启动本地预览..."
    
    cd "$COMPANY_DIR"
    
    # 尝试使用Python启动HTTP服务器
    if command -v python3 &> /dev/null; then
        log "使用Python HTTP服务器 (http://localhost:8080)"
        python3 -m http.server 8080 &
        SERVER_PID=$!
        log "服务器PID: $SERVER_PID"
        log ""
        log "🌐 本地预览地址: http://localhost:8080"
        log "📁 主页面: http://localhost:8080/index_v2.html"
        log "📊 监控页面: http://localhost:8080/stage_monitor_v2.html"
        log ""
        log "按 Ctrl+C 停止服务器"
        wait $SERVER_PID
    else
        log "❌ 未安装Python，无法启动本地服务器"
        exit 1
    fi
}

# 菜单
show_menu() {
    echo ""
    echo "选择部署方式:"
    echo ""
    echo "1) GitHub Pages (免费，推荐)"
    echo "2) Vercel (免费，自动部署)"
    echo "3) Netlify (免费，拖拽部署)"
    echo "4) 本地预览"
    echo "5) 退出"
    echo ""
}

# 主程序
main() {
    check_files
    
    show_menu
    read -p "请输入选项 (1-5): " choice
    
    case $choice in
        1)
            deploy_github
            ;;
        2)
            deploy_vercel
            ;;
        3)
            deploy_netlify
            ;;
        4)
            preview_local
            ;;
        5)
            log "退出部署工具"
            exit 0
            ;;
        *)
            log "❌ 无效选项"
            exit 1
            ;;
    esac
}

# 运行
main
