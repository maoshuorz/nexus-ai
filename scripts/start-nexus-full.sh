#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Nexus AI × Star Office  一键启动脚本
#  用法: bash scripts/start-nexus-full.sh
# ═══════════════════════════════════════════════════════════════
set -e

STAR_OFFICE_DIR="/Users/maoshu/Desktop/tbms/backend/star-office"
NEXUS_DIR="/Users/maoshu/Documents/New project/nexus-ai"
STAR_OFFICE_PORT=18795
STAR_OFFICE_LOG="/tmp/star-office.log"

# ── 颜色 ────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'

info()    { echo -e "  ${GREEN}✓${RESET} $1"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
error()   { echo -e "  ${RED}✗${RESET} $1"; }
section() { echo -e "\n${CYAN}[$1]${RESET} $2"; }

echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │   Nexus AI × Star Office  启动程序      │"
echo "  └─────────────────────────────────────────┘"

# ═══════════════════════════════════════════════════════════════
# 1. Star Office
# ═══════════════════════════════════════════════════════════════
section "1/2" "启动 Star Office 状态看板..."

if lsof -ti ":${STAR_OFFICE_PORT}" > /dev/null 2>&1; then
  info "Star Office 已在运行（端口 ${STAR_OFFICE_PORT}）"
else
  cd "$STAR_OFFICE_DIR"

  # 激活虚拟环境（若存在）
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
  fi

  # 启动服务（后台）
  nohup python app.py > "$STAR_OFFICE_LOG" 2>&1 &
  echo $! > .pid

  # 等待就绪（最多 8 秒）
  for i in $(seq 1 8); do
    sleep 1
    if curl -sf "http://localhost:${STAR_OFFICE_PORT}/health" > /dev/null 2>&1; then
      info "Star Office 启动成功（PID $(cat .pid)）"
      break
    fi
    if [ "$i" -eq 8 ]; then
      error "Star Office 启动失败，查看日志："
      echo "     tail -f ${STAR_OFFICE_LOG}"
      exit 1
    fi
  done
fi

cd "$NEXUS_DIR"

# ═══════════════════════════════════════════════════════════════
# 2. 健康检查
# ═══════════════════════════════════════════════════════════════
section "2/2" "健康检查..."

HEALTH=$(curl -sf "http://localhost:${STAR_OFFICE_PORT}/health" 2>/dev/null || echo "FAIL")
if echo "$HEALTH" | grep -q '"ok"'; then
  info "Star Office /health → OK"
else
  warn "Star Office /health 检查失败"
fi

AGENTS=$(curl -sf "http://localhost:${STAR_OFFICE_PORT}/agents/status" 2>/dev/null || echo "FAIL")
if echo "$AGENTS" | grep -q '"agents"'; then
  COUNT=$(echo "$AGENTS" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('agents',{})))" 2>/dev/null || echo "?")
  info "Agents API → 已注册 ${COUNT} 个 Agent"
else
  warn "Agents API 暂无数据（Agent 启动后自动注册）"
fi

# ═══════════════════════════════════════════════════════════════
# 完成
# ═══════════════════════════════════════════════════════════════
echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │  访问地址                               │"
echo "  │                                         │"
printf "  │  Star Office  → \e[36mhttp://localhost:%-6d\e[0m │\n" "$STAR_OFFICE_PORT"
echo "  │    简洁模式: 查看单 Agent 状态          │"
echo "  │    Agent 模式: 查看 6 Agent 状态墙      │"
echo "  │                                         │"
echo "  │  Star Office 日志: ${STAR_OFFICE_LOG}   │"
echo "  └─────────────────────────────────────────┘"
echo ""
echo "  提示：在 Nexus AI Agent 中调用:"
echo "    self.set_state('writing', '正在分析市场数据')"
echo ""
