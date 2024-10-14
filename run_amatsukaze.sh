#!/bin/zsh

# 设置 PATH，包括常用可执行文件的目录
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/mt/.local/bin"

# 记录当前日期时间到日志
echo "脚本开始执行: $(date)" >> /home/mt/root/exchange/cronjob.log

# 执行你的 Python 脚本，并将输出记录到日志文件
/usr/bin/python3 /home/mt/root/exchange/Amatsukaze.py >> /home/mt/root/exchange/cronjob.log 2>&1

# 记录脚本结束时间到日志
# echo "当前环境变量: $(env)" >> /home/mt/root/exchange/cronjob.log
echo "脚本执行结束: $(date)" >> /home/mt/root/exchange/cronjob.log
