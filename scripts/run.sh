#!/usr/bin/env zsh

# 获取项目根目录
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 日志路径
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/app.log"

# 创建日志目录（如果不存在）
mkdir -p "$LOG_DIR"

# 自定义日志输出函数
log_info() {
  echo "$(date '+%Y-%m-%d %H:%M:%S,%3N') [INFO] scripts.run: $1" >> "$LOG_FILE"
}

log_error() {
  echo "$(date '+%Y-%m-%d %H:%M:%S,%3N') [ERROR] scripts.run: $1" >> "$LOG_FILE"
}

# 输出启动日志
log_info "启动自动化任务"
log_info "执行 app.py"

# 执行 Python 脚本
PYTHONUNBUFFERED=1 /usr/bin/python3 "$BASE_DIR/app.py" >/dev/null 2>&1
STATUS=$?

# 根据状态记录
if [ $STATUS -eq 0 ]; then
  log_info "脚本执行成功"
else
  log_error "脚本执行失败，退出码 $STATUS"
fi

exit $STATUS

# 0 * * * * /usr/bin/zsh /home/mt/root/exchange/scripts/run.sh >> /home/mt/root/exchange/logs/crontab.log 2>&1