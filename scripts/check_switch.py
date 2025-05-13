import sys
import os

# 添加项目根目录到 sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from app.models import AutomationSwitch
from config.settings import get_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=get_engine())
session = Session()
switch = session.query(AutomationSwitch).filter_by(key='auto_enabled').first()
session.close()

# 根据开关状态返回不同退出码
if switch and switch.value:
    exit(0)  # 开启
else:
    exit(1)  # 关闭或不存在
