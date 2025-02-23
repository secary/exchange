import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# 数据库配置
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

CSV_FILE = "/home/mt/root/exchange/data/ExchangeRates.csv"
WEBSITE = "https://www.boc.cn/sourcedb/whpj/"

# 货币列表
CURRENCIES = ["澳大利亚元", "日元"]

# 数据库连接
def get_engine():
    return create_engine(
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    )

# 提醒阈值
CURRENCY_THRESHOLDS = {
    "澳大利亚元": 450
}

# 邮件提醒配置
EMAIL_CONFIG = {
    'sender': os.getenv('EMAIL_SENDER'),
    'password': os.getenv('EMAIL_PASSWORD'),
    'receiver': os.getenv('EMAIL_RECEIVER').split(','),
    'smtp_server': os.getenv('SMTP_SERVER'),
    'smtp_port': int(os.getenv('SMTP_PORT'))
}