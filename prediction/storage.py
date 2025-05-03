import os
import pandas as pd
import time
from sqlalchemy.exc import OperationalError
from config import get_engine, CSV_FILE

def store_data(data_dict):
    all_data = []
    
    # 将字典格式转换为适合 DataFrame 的行数据
    for currency, data in data_dict.items():
        row = {
            "Date": data.get("日期"),
            "Currency": currency,
            "现汇卖出": data.get("现汇卖出价"),
            "Locals": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
        }
        all_data.append(row)

    # 如果没有数据，直接返回
    if not all_data:
        print("未抓取到任何数据，无法存储。")
        return

    # 将数据转换为 Pandas DataFrame
    df_new = pd.DataFrame(all_data)
    df_new = df_new[["Date", "Currency", "现汇卖出", "Locals"]]

    # 如果 CSV 文件存在，读取现有数据并合并
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = df_new

    try:
        # 将数据保存到 CSV 文件
        df_updated.to_csv(CSV_FILE, index=False)
        print(f'数据成功存储到 {CSV_FILE}')

        # 将数据保存到数据库
        df_updated.to_sql('predictions', con=get_engine(), if_exists='append', index=False)
        print('数据成功存储到 exchange.predictions 数据库表')
    except OperationalError as e:
        print(f"数据库操作错误: {e.orig}.")
        if "Can't connect to MySQL server" in str(e.orig):
            print("请检查 MySQL 服务器是否在正确的地址运行")