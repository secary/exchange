import os
import pandas as pd
import time
from sqlalchemy.exc import OperationalError
from config import get_engine, CSV_FILE

def store_data(datalist):
    all_data = []
    for data in datalist:
        if isinstance(data, list):
            data_new = {
                "Currency": [data[0]],
                "现汇买入": [data[1]],
                "现钞买入": [data[2]],
                "现汇卖出": [data[3]],
                "现钞卖出": [data[4]],
                "中行折算": [data[5]],
                "Date": [data[6]],
                "Time": [data[7]],
                "Locals": [time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())]
            }
            all_data.append(data_new)

    if not all_data:
        print("未抓取到任何数据，无法存储。")
        return

    df_new = pd.concat([pd.DataFrame(d) for d in all_data], ignore_index=True)

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = df_new

    try:
        df_updated.to_csv(CSV_FILE, index=False)
        print(f'数据成功存储到 {CSV_FILE}')
        df_updated.to_sql('rates', con=get_engine(), if_exists='replace', index=False)
        print('数据成功存储到 exchange.rates 数据库表')
    except OperationalError as e:
        print(f"数据库操作错误: {e.orig}.")
        if "Can't connect to MySQL server" in str(e.orig):
            print("请检查 MySQL 服务器是否在正确的地址运行")
