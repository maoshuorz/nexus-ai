#!/bin/bash
# Nexus AI - Gmail订单同步定时任务脚本
# 每5分钟执行一次
# 添加到crontab: */5 * * * * /Users/yueqingsong/.openclaw/workspace/company_system/sync_cron.sh

WORKSPACE="/Users/yueqingsong/.openclaw/workspace/company_system"
LOG_FILE="$WORKSPACE/logs/cron_sync.log"
PID_FILE="$WORKSPACE/data/.cron_sync.pid"

# 记录开始时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始同步" >> "$LOG_FILE"

# 检查是否已有实例在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告: 已有同步进程在运行 (PID: $OLD_PID)，跳过" >> "$LOG_FILE"
        exit 0
    fi
fi

# 记录当前PID
echo $$ > "$PID_FILE"

# 执行同步
cd "$WORKSPACE"
/usr/local/bin/python3 "$WORKSPACE/gmail_sync.py" once >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# 检查结果
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 同步成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 同步失败 (退出码: $EXIT_CODE)" >> "$LOG_FILE"
fi

# 清理PID文件
rm -f "$PID_FILE"

echo "---" >> "$LOG_FILE"
