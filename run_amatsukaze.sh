#!/bin/zsh

# 设置 PATH
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/mt/.local/bin:/mnt/c/Windows/System32/WindowsPowerShell/v1.0"

# 定义日志文件和分割线
LOG_FILE="/home/mt/root/exchange/log/amatsu.log"
SEPARATOR1="----------------------------------------"
SEPARATOR2="========================================"

# 获取命令行参数，默认为 1
RUN_PYTHON_SCRIPT=${1:-1}

# 添加分割线和执行时间
echo "$SEPARATOR2" | tee -a "$LOG_FILE"
echo "开启汇率抓取: $(date)" | tee -a "$LOG_FILE"

# 添加分割线并记录 Python 脚本执行
echo "$SEPARATOR1" | tee -a "$LOG_FILE"

# 如果开关为 1，则执行 Python 脚本
if [ "$RUN_PYTHON_SCRIPT" -eq 1 ]; then
  echo "执行 Amatsukaze.py: $(date)" | tee -a "$LOG_FILE"
  # 使用 tee 来同时输出到终端和日志文件
  /usr/bin/python3 /home/mt/root/exchange/Amatsukaze.py | tee -a "$LOG_FILE"
else
  echo "关闭汇率抓取自动化: $(date)" | tee -a "$LOG_FILE"
fi

# 添加分割线并记录结束时间
echo "$SEPARATOR1" | tee -a "$LOG_FILE"
echo "执行结束: $(date)" | tee -a "$LOG_FILE"
echo "$SEPARATOR2" | tee -a "$LOG_FILE"

# 确保脚本退出
exit 0
