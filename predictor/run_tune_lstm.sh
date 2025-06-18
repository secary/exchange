#!/usr/bin/env zsh

# 固定路径
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Jervis.log"
mkdir -p "$LOG_DIR"

# 获取当前脚本文件名
SCRIPT_NAME="$(basename "$0")"

# 生成 Trace ID（兼容无 uuidgen 情况）
if command -v uuidgen >/dev/null 2>&1; then
  TRACE_ID_JERVIS="JERVIS-$(uuidgen)"
else
  TRACE_ID_JERVIS="JERVIS-$(date +%s%N)"
fi
export TRACE_ID_JERVIS


log() {
  local level="$1"
  local msg="$2"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  local line="$timestamp [$level] $SCRIPT_NAME [$TRACE_ID_JERVIS]: $msg"
  echo "$line" | tee -a "$LOG_FILE"
}

log INFO "🧪 开始调参任务"
PYTHON_BIN=$(command -v python3 || echo "/usr/local/bin/python")
PYTHONUNBUFFERED=1 "${PYTHON_BIN}" "$BASE_DIR/predictor/tune_lstm.py"
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "✅ 调参任务完成"
else
  log ERROR "❌ tune_lstm.py 执行失败，退出码 $STATUS"
fi

exit $STATUS
