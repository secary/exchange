#!/bin/zsh

# 获取当前脚本所在目录
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# 定义日志文件路径
LOG_FILE="$BASE_DIR/logs/auto.log"
SEPARATOR1="--------------------------------------------------------------------------------"

# 自动创建 logs 目录（如果不存在）
mkdir -p "$BASE_DIR/logs"

# 添加日志分隔线和时间
echo "$SEPARATOR1" >> "$LOG_FILE"
echo "执行自动化 app.py  $(date)" >> "$LOG_FILE"

# 执行 main.py（使用脚本自身路径）
/usr/bin/python3 "$BASE_DIR/app.py" >> "$LOG_FILE" 2>&1

echo "脚本执行结束: $(date)" >> "$LOG_FILE"
echo "$SEPARATOR1" >> "$LOG_FILE"

exit 0


# 0 * * * * /usr/bin/zsh /home/mt/root/exchange/run.sh >> /home/mt/root/exchange/logs/crontab.log 2>&1