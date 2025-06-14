#!/usr/bin/env zsh

# 项目根目录
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Janus.log"
mkdir -p "$LOG_DIR"

# 获取当前脚本文件名
SCRIPT_NAME="$(basename "$0")"

# 生成 trace_id 并注入全局变量
export TRACE_ID_JANUS="JANUS-$(uuidgen)"

# 日志函数（方法一：显式传入脚本名）
log() {
  local level="$1"
  local script="$2"
  local message="$3"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  local log_line="$timestamp [$level] $script [trace_id=${TRACE_ID_JANUS}]: $message"

  echo "$log_line" >> "$LOG_FILE"
  [[ "$level" == "WARNING" || "$level" == "ERROR" ]] && echo "$log_line"
}

# ✅ 使用时手动传入 $SCRIPT_NAME
log INFO "$SCRIPT_NAME" "🔁 启动自动化任务"
log INFO "$SCRIPT_NAME" "🚀 执行 Janus.py"

PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/Janus.py"
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "$SCRIPT_NAME" "✅ 脚本执行成功"
else
  log ERROR "$SCRIPT_NAME" "❌ 脚本执行失败，退出码 $STATUS"
fi

exit $STATUS
