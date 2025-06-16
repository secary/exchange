import os
import uuid
import pandas as pd
from loguru import logger
from config.logger_config import trace_ids  # ✅ 引入 trace_ids，上下文追踪

# 设置 trace_id（在初始化前设定）
trace_id = os.getenv("TRACE_ID_JANUS") or f"JANUS-{uuid.uuid4()}"
trace_ids["janus"].set(trace_id)

# 绑定 loguru logger（重要：为日志分类添加标识）
logger = logger.bind(name="janus")

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from config.settings import get_engine, CSV_FILE
from utils.models import History
import time

def store_data(data_dict):
    all_data = []

    for currency, data in data_dict.items():
        row = {
            "Date": pd.to_datetime(data.get("日期"), errors="coerce"),
            "Currency": currency,
            "Rate": float(data.get("现汇卖出价")),
            "Locals": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
        }
        all_data.append(row)

    if not all_data:
        logger.warning("未抓取到任何数据，无法存储。")
        return

    df_new = pd.DataFrame(all_data)

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = df_new

    # try:
    #     df_updated.to_csv(CSV_FILE, index=False)
    #     logger.info(f"✅ 数据成功存储到 {CSV_FILE}")
    # except Exception as e:
    #     logger.error(f"❌ csv保存错误: {e}")

    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for row in all_data:
            existing = session.query(History).filter_by(Date=row["Date"], Currency=row["Currency"]).first()
            if existing:
                existing.Locals = row["Locals"]
            else:
                new_entry = History(**row)
                session.add(new_entry)
        session.commit()
        logger.info("✅ 数据成功更新到 exchange.history 数据库表")
    except OperationalError as e:
        session.rollback()
        logger.error(f"❌ 数据库操作错误: {e.orig}")
        if "Can't connect to MySQL server" in str(e.orig):
            logger.warning("请检查 MySQL 服务器是否在正确的地址运行")
    except Exception as e:
        session.rollback()
        logger.exception(f"❌ 其他错误: {e}")
    finally:
        session.close()
