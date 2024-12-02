#!/bin/zsh

# 设置 PATH
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/mt/.local/bin:/mnt/c/Windows/System32/WindowsPowerShell/v1.0"

# 定义日志文件和分割线
LOG_FILE="/home/mt/root/exchange/log/amatsu.log"
SEPARATOR1="----------------------------------------"
SEPARATOR2="========================================"

# 添加分割线和执行时间
echo "$SEPARATOR2" >> "$LOG_FILE"
echo "脚本开始执行: $(date)" >> "$LOG_FILE"

# 添加分割线并记录 Python 脚本执行
echo "$SEPARATOR1" >> "$LOG_FILE"
# echo "执行 Python 脚本: $(date)" >> "$LOG_FILE"
/usr/bin/python3 /home/mt/root/exchange/Amatsukaze.py >> "$LOG_FILE" 2>&1

# 添加分割线并记录结束时间
echo "$SEPARATOR1" >> "$LOG_FILE"
echo "脚本执行结束: $(date)" >> "$LOG_FILE"
echo "$SEPARATOR2" >> "$LOG_FILE"
