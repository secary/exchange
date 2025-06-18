import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
from loguru import logger
from config.logger_config import trace_ids  # ✅ 引入 trace_ids，上下文追踪

# 设置 trace_id（在初始化前设定）
trace_id = os.getenv("TRACE_ID_JANUS") or f"JANUS-{uuid.uuid4()}"
trace_ids["janus"].set(trace_id)

# 绑定 loguru logger（重要：为日志分类添加标识）
logger = logger.bind(name="janus")

import urllib.request
import urllib.error
import traceback
from bs4 import BeautifulSoup
import time
import random

# 多个 User-Agent 列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    'Mozilla/5.0 (X11; Linux x86_64)...',
]

from utils.models import CurrencyMap
from sqlalchemy.orm import sessionmaker
from config.settings import get_engine

# 在函数外初始化一次
Session = sessionmaker(bind=get_engine())
session = Session()
rows = session.query(CurrencyMap).all()
CN2EN = { r.name_cn: r.code_en for r in rows }
session.close()

def askurl(url, timeout=15, retries=3, delay=10):
    import socket
    socket.setdefaulttimeout(timeout)

    for attempt in range(1, retries + 1):
        user_agent = random.choice(USER_AGENTS)
        headers = {'User-Agent': user_agent}
        request = urllib.request.Request(url, headers=headers)

        try:
            logger.debug(f" 第 {attempt} 次尝试，URL: {url}, UA: {user_agent}")
            response = urllib.request.urlopen(request, timeout=timeout)
            html = response.read().decode('utf-8')
            logger.debug(f" ✅ 成功，第 {attempt} 次，请求状态码: {response.getcode()}")
            return html

        except urllib.error.HTTPError as e:
            logger.warning(f" ⚠️ 第 {attempt} 次失败 - HTTPError: {e.code}, {e.reason}")
            logger.debug(f" 响应头: {e.headers}")
        except urllib.error.URLError as e:
            logger.warning(f" ⚠️ 第 {attempt} 次失败 - URLError: {e.reason}")
        except TimeoutError as e:
            logger.warning(f" ⚠️ 第 {attempt} 次失败 - TimeoutError: {e}")
        except Exception:
            logger.exception(f" ❌ 第 {attempt} 次失败 - 未知异常")
            logger.debug(traceback.format_exc())

        if attempt < retries:
            sleep_time = delay + random.uniform(2, 5)
            logger.info(f" 将在 {sleep_time:.1f} 秒后重试...")

    logger.error(f" ❌ 所有 {retries} 次尝试均失败，放弃请求。")
    return None

def get_exchange_rate(url, currencies, save_html=False):
    if not isinstance(currencies, list):
        logger.error("❌ currencies 参数必须是一个列表")
        return {}

    html = askurl(url)
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
            
    if save_html:
        timestamp = time.strftime("%Y%m%d_%H%M%S")  # 正确、安全的时间格式
        file = f'source_{timestamp}.html'
        path = os.path.join('data', 'source', file)
        os.makedirs(os.path.dirname(path), exist_ok=True)  # 确保目录存在
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"📁 html源文件已保存至 {path}")

    logger.debug(f"汇率抓取结果: {result}")
    return result

