#!/usr/bin/env zsh

echo "TZ=Australia/Adelaide" >> /etc/environment

# 安全注入环境变量供 cron 使用
printenv | grep -E 'DB_USER|DB_PASSWORD|DB_HOST|DB_NAME' >> /etc/environment

# 注册定时任务
crontab /Janus/crontab.txt

# 启动 cron（前台）
exec cron -f
