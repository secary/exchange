import sys
import os

# 添加项目根目录到 sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# 现在可以导入 app 模块
from utils.models import Base
from config.settings import get_engine

from sqlalchemy import create_engine
from utils.models import Base  # 包含你刚定义的 Prediction 类
from config.settings import get_engine  # 你项目已有的配置
  
def main():

    # 获取数据库连接
    engine = get_engine()

    # 创建所有定义的表（如果不存在）
    Base.metadata.create_all(engine)
    
if __name__ == "__main__":
    main()
    print("✅ 数据库表已刷新")