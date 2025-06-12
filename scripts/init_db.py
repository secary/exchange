# init_db.py
import sys
import os

# 添加项目根目录到 sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import logging.config
from config.logger_config import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

from app.models import Base, Threshold, AutomationSwitch
from config.settings import get_engine
from sqlalchemy.orm import sessionmaker

engine = get_engine()
Base.metadata.create_all(engine)
logger.info("✅ 所有表创建成功")

Session = sessionmaker(bind=engine)
session = Session()

# 防止重复插入
thresholds_to_add = [
    {"Currency": "澳大利亚元", "Upper": 500.0, "Lower": 450.0},
    {"Currency": "日元", "Upper": 6.0, "Lower": 4.5}
]

for t in thresholds_to_add:
    if not session.query(Threshold).filter_by(Currency=t["Currency"]).first():
        session.add(Threshold(**t))
    else:
        logger.info(f"⚠️ 已存在: {t['Currency']}，跳过插入")

session.commit()
session.close()
logger.info("✅ 初始阈值已写入")

# 初始化开关状态为 True
Session = sessionmaker(bind=engine)
session = Session()
session.merge(AutomationSwitch(key='auto_enabled', value=True))  # merge 会更新或插入
session.commit()
session.close()