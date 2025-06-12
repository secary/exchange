import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import time

import random
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


# 多个 User-Agent 列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    'Mozilla/5.0 (X11; Linux x86_64)...',
]

from app.models import CurrencyMap
from sqlalchemy.orm import sessionmaker
from config.settings import get_engine

# 在函数外初始化一次
Session = sessionmaker(bind=get_engine())
session = Session()
rows = session.query(CurrencyMap).all()
CN2EN = { r.name_cn: r.code_en for r in rows }
session.close()

def askurl(url, timeout=15, retries=3, delay=10):
    for attempt in range(1, retries + 1):
        user_agent = random.choice(USER_AGENTS)
        headers = {'User-Agent': user_agent}
        request = urllib.request.Request(url, headers=headers)

        try:
            response = urllib.request.urlopen(request, timeout=timeout)
            html = response.read().decode('utf-8')
            logger.debug(f"✅ 第 {attempt} 次请求成功，User-Agent: {user_agent}")
            return html
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            logger.warning(f"第 {attempt} 次请求失败，原因: {e}")
        except Exception as e:
            logger.exception(f"第 {attempt} 次请求发生意外错误: {e}")

        if attempt < retries:
            sleep_time = delay + random.uniform(2, 5)
            logger.info(f"将在 {sleep_time:.1f} 秒后重试...")
            time.sleep(sleep_time)

    logger.error(f"❌ 所有 {retries} 次尝试均失败，放弃请求。")
    return None

def get_exchange_rate(url, currencies, timeout=15, retries=2, delay=10):
    if not isinstance(currencies, list):
        logger.error("❌ currencies 参数必须是一个列表")
        return {}

    html = askurl(url, timeout=timeout, retries=retries, delay=delay)
    if not html:
        logger.error("❌ 未能获取 HTML 内容")
        return {}
    
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    for currency in currencies:
        target_td = soup.find('td', string=currency)
        if target_td:
            row = target_td.find_parent('tr')
            row_data = [td.get_text(strip=True) for td in row.find_all('td')]
            name_cn = row_data[0]
            name_en = CN2EN.get(name_cn, name_cn)
            result[name_en] = {
                "现汇卖出价": row_data[3],
                "日期": row_data[6]
            }
        else:
            logger.warning(f"❌ 未找到包含 '{currency}' 的 <td> 标签")

    if not result:
        os.makedirs("data", exist_ok=True)
        failed_path = os.path.join("data", "failed_response.html")
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.warning(f"⚠️ 抓取失败，原始 HTML 已保存到 {failed_path}")

    logger.debug(f"汇率抓取结果: {result}")
    return result

