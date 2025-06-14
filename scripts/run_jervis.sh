#!/usr/bin/env zsh

# 固定路径
BASE_DIR="/home/mt/root/Janus"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Jervis.log"
mkdir -p "$LOG_DIR"

SCRIPT_NAME="$(basename "$0")"
export TRACE_ID_JERVIS="JERVIS-$(uuidgen)"

# ✅ 所有日志仅写入 Jervis.log，不输出终端
log() {
  local level="$1"
  local message="$2"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  echo "$timestamp [$level] $SCRIPT_NAME [trace_id=${TRACE_ID_JERVIS}]: $message" >> "$LOG_FILE"
}

log INFO "⏰ 启动每日预测任务"
log INFO "🚀 执行 Jervis.py"

# ✅ 静默运行 Python，只由 loguru 写入 Jervis.log
PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/Jervis.py" >/dev/null 2>&1
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "✅ 预测任务完成"
else
  log ERROR "❌ Jervis.py 执行失败，退出码 $STATUS"
fi

exit $STATUS
