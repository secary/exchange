from fetcher import get_exchange_rate
from storage import store_data
from config import WEBSITE,CURRENCIES
import pandas as pd

def main():
    try:
        print(f"开始抓取人民币兑换 {', '.join(CURRENCIES)} 汇率数据")
        print(f"数据来源：{WEBSITE}")
        rates_data = get_exchange_rate(WEBSITE, CURRENCIES)
        store_data(rates_data)
        print("汇率数据抓取完成")

        # 转换为 Pandas DataFrame
        df = pd.DataFrame(rates_data)
        print(df)

    except Exception as e:
        print(f"出现错误：{e}")

if __name__ == '__main__':
    main()
