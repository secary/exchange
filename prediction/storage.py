import os
import pandas as pd
import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from config import get_engine, CSV_FILE

def store_data(data_dict):
    all_data = []

    for currency, data in data_dict.items():
        row = {
            "Date": data.get("日期"),
            "Currency": currency,
            "现汇卖出": data.get("现汇卖出价"),
            "Locals": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
        }
        all_data.append(row)

    if not all_data:
        print("未抓取到任何数据，无法存储。")
        return

    df_new = pd.DataFrame(all_data)
    df_new = df_new[["Date", "Currency", "现汇卖出", "Locals"]]
    df_new["Date"] = pd.to_datetime(df_new["Date"], errors="coerce")


    # # 合并 CSV（历史数据管理）
    # if os.path.exists(CSV_FILE):
    #     df_existing = pd.read_csv(CSV_FILE)
    #     df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    # else:
    #     df_updated = df_new

    # # 保存合并后的 CSV
    # df_updated.to_csv(CSV_FILE, index=False)
    # print(f'数据成功存储到 {CSV_FILE}')

    # 插入到数据库并根据主键更新 Locals
    engine = get_engine()
    sql = text("""
        INSERT INTO predictions (`Date`, `Currency`, `现汇卖出`, `Locals`)
        VALUES (:Date, :Currency, :Sell, :Locals)
        ON DUPLICATE KEY UPDATE `Locals` = VALUES(`Locals`);
    """)

    try:
        with engine.begin() as conn:
            for row in df_new.itertuples(index=False, name=None):
                conn.execute(sql, {
                    "Date": row[0],
                    "Currency": row[1],
                    "Sell": row[2],
                    "Locals": row[3]
                })
        print("数据成功更新到 exchange.predictions 数据库表")

    except OperationalError as e:
        print(f"数据库操作错误: {e.orig}.")
        if "Can't connect to MySQL server" in str(e.orig):
            print("请检查 MySQL 服务器是否在正确的地址运行")
