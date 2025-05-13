import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import time
import os
import logging.config
from config.logger_config import LOGGING_CONFIG

# ✅ 清除之前的 handler，防止重复日志
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("service")

def askurl(url, timeout=10, retries=3, delay=2):
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=head)

    for attempt in range(1, retries + 1):
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
            html = response.read().decode('utf-8')
            return html
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            logger.warning(f"第 {attempt} 次请求失败: {e}")
        except Exception as e:
            logger.exception(f"第 {attempt} 次请求发生意外错误: {e}")
        if attempt < retries:
            logger.info(f"将在 {delay} 秒后重试...")
            time.sleep(delay)

    logger.error(f"❌ 所有 {retries} 次尝试均失败，放弃请求。")
    return None

def get_exchange_rate(url, currencies, timeout=20, retries=3):
    if not isinstance(currencies, list):
        raise ValueError("❌ currencies 参数必须是一个列表")
    
    html = askurl(url, timeout=timeout, retries=retries)
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
            result[row_data[0]] = {
                "现汇卖出价": row_data[3],
                "日期": row_data[6]
            }
        else:
            logger.warning(f"❌ 未找到包含 '{currency}' 的 <td> 标签")

    if not result:
        # 保存 HTML 到 data/failed_response.html
        os.makedirs("data", exist_ok=True)
        failed_path = os.path.join("data", "failed_response.html")
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.warning(f"⚠️ 抓取失败，原始 HTML 已保存到 {failed_path}")

    logger.debug(f"汇率抓取结果: {result}")
    
    return result
