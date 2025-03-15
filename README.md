# MT's Exchange Rate Web Crawler
## 概述
* 中行外汇汇率数据爬取，数据源：[链接](https://www.boc.cn/sourcedb/whpj/)
## 功能
* 可以通过配置crontab来进行自动化
* 通过i.sh或o.sh来控制自动化任务开关
* 当前为抓取澳元与日元汇率，主要执行脚本为Amatsukaze.py
* 可以根据阈值需求设置弹窗提醒或邮箱提醒，需要自己配置环境变量
* 执行记录会保存至log目录