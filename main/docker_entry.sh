#!/usr/bin/env zsh

set -e

# 设置时区（只添加一次）
if ! grep -q '^TZ=' /etc/environment; then
  echo "TZ=Australia/Adelaide" >> /etc/environment
fi
export TZ=Australia/Adelaide

# 注入 DB 环境变量到 /etc/environment（避免重复写入）
for var in DB_USER DB_PASSWORD DB_HOST DB_NAME; do
  if printenv "$var" >/dev/null 2>&1; then
    grep -q "^$var=" /etc/environment || echo "$var=$(printenv $var)" >> /etc/environment
  fi
done

# 注册 crontab（防止重复添加）
crontab /Janus/crontab.txt

# 启动 cron 服务（前台）
exec cron -f
