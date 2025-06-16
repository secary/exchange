#!/usr/bin/env zsh

# 项目根目录
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Janus.log"
mkdir -p "$LOG_DIR"

SCRIPT_NAME="$(basename "$0")"
export TRACE_ID_JANUS="JANUS-$(uuidgen)"

log() {
  local level="$1"
  local message="$2"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  echo "$timestamp [$level] $SCRIPT_NAME [${TRACE_ID_JANUS}]: $message" | tee -a "$LOG_FILE"
}

log INFO "🔁 启动自动化任务"
log INFO "🚀 执行 Janus.py"

# ✅ 执行 Python，但不写 stdout/stderr，只写 loguru
PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/main/Janus.py" 

STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "✅ 脚本执行成功"
else
  log ERROR "❌ 脚本执行失败，退出码 $STATUS"
fi

exit $STATUS
