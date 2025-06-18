import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
import pandas as pd
from loguru import logger
from config.logger_config import trace_ids  # ✅ 引入 trace_ids，上下文追踪

# 设置 trace_id（在初始化前设定）
trace_id = os.getenv("TRACE_ID_JANUS") or f"JANUS-{uuid.uuid4()}"
trace_ids["janus"].set(trace_id)

# 绑定 loguru logger（重要：为日志分类添加标识）
logger = logger.bind(name="janus")

# 模块功能导入
from fetcher import get_exchange_rate
from storage import store_data
from config.settings import WEBSITE, CURRENCIES


def main():
    try:
        logger.info(f"⚓ 开始抓取人民币兑换 {', '.join(CURRENCIES)} 汇率数据")
        
        rates_data = get_exchange_rate(WEBSITE, CURRENCIES)
        if not rates_data:
            logger.warning("⚠️ 未获取任何汇率数据")
            return

        store_data(rates_data)
        logger.info("汇率数据抓取完成")

        # 输出数据为 DataFrame
        df = pd.DataFrame(rates_data)
        print(f"当前汇率：\n{df}")

    except Exception as e:
        logger.exception(f"❌ 出现错误：{e}")

if __name__ == '__main__':
    logger.info("Janus、了解！任せなさい！")
    main()
