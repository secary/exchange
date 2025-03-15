export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/mt/.local/bin:/mnt/c/Windows/System32/WindowsPowerShell/v1.0"

# 定义日志文件和分割线
LOG_FILE="/home/mt/root/exchange/log/amatsu.log"
SEPARATOR1="--------------------------------------------------------------------------------"
SEPARATOR2="================================================================================"

# 添加分割线并记录脚本执行时间
echo "$SEPARATOR2" >> "$LOG_FILE"
echo "开始抓取汇率: $(date)" >> "$LOG_FILE"

echo "$SEPARATOR1" >> "$LOG_FILE"
echo "执行 Amatsukaze.py: $(date)" >> "$LOG_FILE"
# 执行python脚本
/usr/bin/python3 /home/mt/root/exchange/Amatsukaze.py >> "$LOG_FILE" 2>&1

# 添加分割线并记录结束时间
echo "$SEPARATOR1" >> "$LOG_FILE"
echo "脚本执行结束: $(date)" >> "$LOG_FILE"
echo "$SEPARATOR2" >> "$LOG_FILE"

# 确保脚本退出
exit 0

