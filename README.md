# MT's Exchange Rate Web Crawler
* 中行外汇汇率数据爬取，数据源：[链接](https://www.boc.cn/sourcedb/whpj/)
* 通过wsl的crontab设置自动化运行，运行周期为60分钟一次
* 数据保存至data文件夹及个人数据库，需要的时候直接调用数据库或从data文件夹下载
* Amatsukaze.py为爬虫程序，run_amastsukaze.sh则是为了自动化运行中保存日志