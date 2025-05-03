export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/mt/.local/bin:/mnt/c/Windows/System32/WindowsPowerShell/v1.0"

# 定义日志文件和分割线
LOG_FILE="prediction/logs/exchange.log"
SEPARATOR1="--------------------------------------------------------------------------------"
SEPARATOR2="================================================================================"

# 添加分割线并记录脚本执行时间
echo "$SEPARATOR1" >> "$LOG_FILE"
echo "执行 main.py $(date)" >> "$LOG_FILE"
# 执行python脚本
/usr/bin/python3 /home/mt/root/exchange/prediction/main.py >> "$LOG_FILE" 2>&1

echo "脚本执行结束: $(date)" >> "$LOG_FILE"
echo "$SEPARATOR1" >> "$LOG_FILE"

# 确保脚本退出
exit 0

# 0 * * * * /bin/bash /home/mt/root/exchange/prediction/run.sh >> /home/mt/root/exchange/prediction/crontab.log 2>&1
