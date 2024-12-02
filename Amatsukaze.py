
from fetcher import get_exchange_rate
from storage import store_data
from notifier import send_notification
from config import WEBSITE,CURRENCIES, CURRENCY_THRESHOLDS


def main():
    try:
        print(f"开始抓取人民币兑换 {', '.join(CURRENCIES)} 汇率数据")
        rates_data = get_exchange_rate(WEBSITE, CURRENCIES)
        store_data(rates_data)
        print("汇率数据抓取完成")
        print(f'{rates_data[0][0]}现汇价：{rates_data[0][1]}')
        print(f'{rates_data[1][0]}现汇价：{rates_data[1][1]}')
        
        # 遍历抓取到的汇率数据，检查是否需要提醒
        for data in rates_data:
            if isinstance(data, list) and len(data) > 1:
                currency = data[0]
                exchange_rate = float(data[1])  # 假设抓取的汇率是第二列

                # 根据字典中的阈值判断是否需要提醒
                threshold = CURRENCY_THRESHOLDS.get(currency)
                if threshold is not None and exchange_rate < threshold:
                    message = f"{currency}当前汇率为: {exchange_rate}，低于{threshold}，抓紧买！"
                    print(message)

                    # 发送弹窗通知
                    send_notification("汇率提醒", message)
                    
    except Exception as e:
        print(f"出现错误：{e}")

if __name__ == '__main__':
    main()
