# MT's Exchange Rate Web Crawler
## 概述
* 中行外汇汇率数据爬取，数据源：[链接](https://www.boc.cn/sourcedb/whpj/)
* 通过wsl的crontab设置自动化运行，运行周期为30分钟一次
* 数据保存至data文件夹及个人数据库
## 功能介绍
* 通过shell脚本运行以便保存日志
* 设置config.py以进行阈值警告，汇率低于阈值时可以自动通知
* 通知通过调用powershell的BurnToast实现弹窗，以及python的smtplib群发邮件
* 拆分主逻辑模块与其他功能模块
## 卫星
* 分析功能建设中