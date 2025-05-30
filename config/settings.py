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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "ExchangeRates.csv")
WEBSITE = "https://www.boc.cn/sourcedb/whpj/"

# 货币列表
CURRENCIES = ["澳大利亚元", "日元"]

# 数据库连接
def get_engine():
    return create_engine(
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    )

