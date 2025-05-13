# scripts/set_switch.py
import sys
import os

# 添加项目根目录到 sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import logging.config
from config.logger_config import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("auto")


from sqlalchemy.orm import sessionmaker
from config.settings import get_engine
from app.models import AutomationSwitch

def set_switch(status: bool):
    Session = sessionmaker(bind=get_engine())
    session = Session()
    session.merge(AutomationSwitch(key='auto_enabled', value=status))
    session.commit()
    session.close()
    logger.info(f"✅ 自动化开关已设置为: {'开启' if status else '关闭'}")

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ['on', 'off']:
        logger.info("用法: python set_switch.py [on|off]")
        sys.exit(1)

    status = sys.argv[1] == 'on'
    set_switch(status)
