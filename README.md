# MT's Exchange Rate Web Crawler
## 概述
* 中行外汇汇率数据爬取，数据源：[链接](https://www.boc.cn/sourcedb/whpj/)
* 仅抓取现汇卖出数据
## 功能
* 通过crontab配置自动化以方便预测
* 保存至本地和数据库
## 卫星
* 通过Flask框架构建前端展示，包含可视化，自动化开关等功能
* 利用LSTM或Arima等神经网络时间序列分析尝试预测