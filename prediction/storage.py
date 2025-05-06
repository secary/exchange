import pandas as pd
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import get_engine, CSV_FILE
from models import Prediction, Base

def store_data(data_dict):
    all_data = []

    for currency, data in data_dict.items():
        row = {
            "Date": pd.to_datetime(data.get("日期"), errors="coerce"),
            "Currency": currency,
            "现汇卖出": float(data.get("现汇卖出价")),
            "Locals": pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        }
        all_data.append(row)

    if not all_data:
        print("未抓取到任何数据，无法存储。")
        return

    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for row in all_data:
            existing = session.query(Prediction).filter_by(Date=row["Date"], Currency=row["Currency"]).first()
            if existing:
                existing.Locals = row["Locals"]
            else:
                new_entry = Prediction(**row)
                session.add(new_entry)
        session.commit()
        print("数据成功更新到 exchange.predictions 数据库表")

    except OperationalError as e:
        session.rollback()
        print(f"数据库操作错误: {e.orig}.")
        if "Can't connect to MySQL server" in str(e.orig):
            print("请检查 MySQL 服务器是否在正确的地址运行")
    except Exception as e:
        session.rollback()
        print(f"其他错误: {e}")
    finally:
        session.close()
