# 💱 Janus 
🌐 Hi！私の名前はJanus!  

本项目是一个端到端的汇率数据平台，涵盖了汇率抓取、存储、预测与可视化展示，支持容器化部署与定时任务执行。

---

## 📁 项目结构

```
.
├── .env.example            # 环境变量模板
├── README.md               # 项目说明文件
├── requirements.txt        # Python 依赖包
│
├── config/                 # 配置文件
│   ├── logger_config.py
│   └── settings.py
│
├── Docker/                 # Docker 配置
│   ├── docker-compose.yaml
│   ├── Dockerfile.Janus
│   └── Dockerfile.Javelin
│
├── main/                   # 汇率抓取模块
│   ├── fetcher.py
│   ├── Janus.py            # 主入口
│   ├── notifier.py
│   ├── run_janus.sh
│   └── storage.py
│
├── predictor/              # 预测模型模块
│   ├── Jervis.py           # 主预测入口
│   ├── methods.py
│   ├── run_jervis.sh
│   ├── run_tune_lstm.sh
│   ├── tune_lstm.py        # LSTM 调参逻辑
│   └── models/
│       ├── base.py
│       ├── lstm.py
│       └── __init__.py
│
├── utils/                  # 辅助工具
│   ├── createdb.py         # 初始化数据库
│   └── models.py           # ORM 模型定义
│
└── web/                    # Web 前端接口
    ├── Javelin.py          # Flask 启动脚本
    └── app/
        ├── routes.py
        ├── __init__.py
        └── templates/
            ├── index.html
            └── history.html
```

---

## ⚙️ 功能概述

| 模块 | 功能 |
|------|------|
| `Janus` | 抓取中国银行网页汇率数据并写入数据库与 CSV |
| `Jervis` | 使用 LSTM 模型预测汇率 |
| `Javelin` | 提供基于 Flask 的可视化网页与 REST 接口 |
| `notifier.py` | 可拓展的通知模块（如钉钉、邮件） |
| `run_*.sh` | 提供 cron 等任务调用支持 |
| `Docker` | 快速部署，模块化构建 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 `.env`

```env
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_NAME=exchange
```

### 3. 初始化数据库

```bash
python utils/createdb.py
```

### 4. 运行各个模块

```bash
python main/Janus.py         # 抓取汇率
python predictor/Jervis.py   # 预测汇率
python web/Javelin.py        # 启动 Flask 前端
```

---

## 🐳 Docker 部署（可选）

```bash
cd Docker
docker-compose up --build
```

---

## 📈 Web 页面预览

- `index.html`：显示预测图与最新汇率
- `history.html`：表格形式展示历史汇率与阈值变化

访问路径通常为：

```
http://localhost:5000/
```

---

## 🕒 定时任务支持

通过 crontab 配置自动抓取/预测：

```
0 9 * * * /usr/bin/zsh /path/to/run_janus.sh
0 10 * * * /usr/bin/zsh /path/to/run_jervis.sh
```

---