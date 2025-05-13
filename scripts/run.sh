#!/usr/bin/env zsh

# 获取项目根目录
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 日志路径
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/auto.log"

mkdir -p "$LOG_DIR"

log_info() {
  echo "$(date '+%Y-%m-%d %H:%M:%S,%3N') [INFO] scripts.run: $1" >> "$LOG_FILE"
}

log_error() {
  echo "$(date '+%Y-%m-%d %H:%M:%S,%3N') [ERROR] scripts.run: $1" >> "$LOG_FILE"
}

# 检查自动化开关
PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/scripts/check_switch.py"
if [ $? -ne 0 ]; then
  exit 0
fi

log_info "启动自动化任务"
log_info "执行 Janus.py"

# 执行主程序
PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/Janus.py" >/dev/null 2>&1
STATUS=$?

if [ $STATUS -eq 0 ]; then
  log_info "脚本执行成功"
else
  log_error "脚本执行失败，退出码 $STATUS"
fi

exit $STATUS

# 0 * * * * /usr/bin/zsh /home/mt/root/Janus/scripts/run.sh >> /home/mt/root/Janus/logs/crontab.log 2>&1