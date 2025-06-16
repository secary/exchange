#!/usr/bin/env zsh

# 项目根目录
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Janus.log"
mkdir -p "$LOG_DIR"

SCRIPT_NAME="$(basename "$0")"

# 生成 Trace ID（兼容无 uuidgen 情况）
if command -v uuidgen >/dev/null 2>&1; then
  TRACE_ID_JANUS="JANUS-$(uuidgen)"
else
  TRACE_ID_JANUS="JANUS-$(date +%s%N)"
fi
export TRACE_ID_JANUS

log() {
  local level="$1"
  local message="$2"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  echo "$timestamp [$level] $SCRIPT_NAME [${TRACE_ID_JANUS}]: $message" | tee -a "$LOG_FILE"
}

log INFO "🔁 启动自动化任务"

PYTHON_BIN=$(command -v python3 || echo "/usr/local/bin/python")

PYTHONUNBUFFERED=1 "$PYTHON_BIN" "$BASE_DIR/main/Janus.py"
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "✅ 脚本执行成功"
else
  log ERROR "❌ 脚本执行失败，退出码 $STATUS"
fi

exit $STATUS
