#!/usr/bin/env zsh

cd /home/mt/root/Janus || exit 1

LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/Jervis.log"

mkdir -p "$LOG_DIR"

# 获取当前脚本文件名
SCRIPT_NAME="$(basename "$0")"

export TRACE_ID_JERVIS="JERVIS-$(uuidgen)"

log() {
  local level="$1"
  local msg="$2"
  local timestamp="$(date '+%Y-%m-%d %H:%M:%S,%3N')"
  local line="$timestamp [$level] $SCRIPT_NAME [$TRACE_ID_JERVIS]: $msg"

  echo "$line" >> "$LOG_FILE"
  [[ "$level" == "WARNING" || "$level" == "ERROR" ]] && echo "$line"
}

log INFO "🧪 开始调参任务"
PYTHONUNBUFFERED=1 /usr/bin/python3 ./app/prediction/tune_lstm.py
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log INFO "✅ 调参任务完成"
else
  log ERROR "❌ tune_lstm.py 执行失败，退出码 $STATUS"
fi

exit $STATUS
