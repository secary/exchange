#!/usr/bin/env zsh

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Janus.log"
mkdir -p "$LOG_DIR"

# 生成 trace_id 并注入全局变量
export TRACE_ID_JANUS="JANUS-$(uuidgen)"

log() {
  local level="$1"
  local msg="$2"
  echo "$(date '+%Y-%m-%d %H:%M:%S,%3N') [$level] run.sh [trace_id=${TRACE_ID_JANUS}]: $msg" >> "$LOG_FILE"
}

log INFO "🔁 启动自动化任务"
log INFO "🚀 执行 Janus.py"

PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/Janus.py"
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "✅ 脚本执行成功"
else
  log ERROR "❌ 脚本执行失败，退出码 $STATUS"
fi

exit $STATUS
