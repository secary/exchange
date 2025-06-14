#!/usr/bin/env zsh

# 固定项目路径（你明确指定了）
BASE_DIR="/home/mt/root/Janus"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/Jervis.log"

mkdir -p "$LOG_DIR"

# 获取当前脚本文件名
SCRIPT_NAME="$(basename "$0")"

# 生成 trace_id 并注入全局变量
export TRACE_ID_JERVIS="JERVIS-$(uuidgen)"

# 日志函数（风格与你完全一致）
log() {
  local level="$1"
  local script="$2"
  local message="$3"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  local log_line="$timestamp [$level] $script [trace_id=${TRACE_ID_JERVIS}]: $message"

  # 所有日志写入文件
  echo "$log_line" >> "$LOG_FILE"

  # 仅 WARNING 和 ERROR 输出到终端
  case "$level" in
    WARNING|ERROR)
      echo "$log_line" ;;
  esac
}

# ✅ 使用时传入 $SCRIPT_NAME
log INFO "$SCRIPT_NAME" "⏰ 启动每日预测任务"
log INFO "$SCRIPT_NAME" "🚀 执行 Jervis.py"

PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/Jervis.py"
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "$SCRIPT_NAME" "✅ 预测任务完成"
else
  log ERROR "$SCRIPT_NAME" "❌ Jervis.py 执行失败，退出码 $STATUS"
fi

exit $STATUS
