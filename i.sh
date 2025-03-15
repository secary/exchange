# !/bin/zsh
# Open CronTab 
echo 1 > io
echo "Crontab自动化抓取汇率任务已开启: $(date)" | tee -a log/amatsu.log
echo "================================================================================" >> log/amatsu.log