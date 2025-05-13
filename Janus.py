import logging.config
from config.logger_config import LOGGING_CONFIG

logging.getLogger("service").handlers.clear()
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.debug("日志配置初始化成功")

from app.services.fetcher import get_exchange_rate
from app.services.storage import store_data
from config.settings import WEBSITE, CURRENCIES
import pandas as pd


def main():
    try:
        logger.info(f"开始抓取人民币兑换{', '.join(CURRENCIES)}汇率数据")
        logger.info(f"数据来源：{WEBSITE}")
        
        rates_data = get_exchange_rate(WEBSITE, CURRENCIES)
        store_data(rates_data)

        logger.info("汇率数据抓取完成")

        # 转换为 Pandas DataFrame 并输出日志
        df = pd.DataFrame(rates_data)
        logger.info(f"抓取数据内容：\n{df}")

    except Exception as e:
        logger.exception(f"❌ 出现错误：{e}")  # 自动包含堆栈信息

if __name__ == '__main__':
    logger.info("Janus、了解！任せなさい！")
    main()
