# !/bin/zsh
# Close CronTab
echo 0 > io
echo "Crontab自动化抓取汇率任务已关闭: $(date)" | tee -a log/amatsu.log
echo "================================================================================" >> log/amatsu.log
