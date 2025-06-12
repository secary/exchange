import os
import uuid
import logging.config
from config.logger_config import LOGGING_CONFIG, trace_ids

# 🚨 一定要在 loggers 初始化前设置 trace_id
trace_id_from_env = os.getenv("TRACE_ID")
if trace_id_from_env:
    trace_ids["janus"].set(trace_id_from_env)
else:
    trace_ids["janus"].set(f"JANUS-{uuid.uuid4()}")  # fallback only if not set

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("janus")

# 模块功能导入
from app.services.fetcher import get_exchange_rate
from app.services.storage import store_data
from config.settings import WEBSITE, CURRENCIES
import pandas as pd


def main():
    try:
        logger.info(f"开始抓取人民币兑换 {', '.join(CURRENCIES)} 汇率数据")
        logger.info(f"数据来源：{WEBSITE}")
        
        rates_data = get_exchange_rate(WEBSITE, CURRENCIES)
        store_data(rates_data)

        logger.info("汇率数据抓取完成")

        # 输出数据为 DataFrame
        df = pd.DataFrame(rates_data)
        print(f"当前汇率：\n{df}")

    except Exception as e:
        logger.exception(f"❌ 出现错误：{e}")  # 包含堆栈 trace_id

if __name__ == '__main__':
    logger.info("Janus、了解！任せなさい！")
    main()
