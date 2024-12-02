from fetcher import get_exchange_rate
from storage import store_data
from notifier import send_notification, send_email
from config import WEBSITE,CURRENCIES, CURRENCY_THRESHOLDS, EMAIL_CONFIG
import pandas as pd


def main():
    try:
        print(f'开始抓取人民币兑换 {", ".join(CURRENCIES)} 汇率数据')
        print(f'数据来源：{WEBSITE}')
        rates_data = get_exchange_rate(WEBSITE, CURRENCIES)
        store_data(rates_data)
        print('汇率数据抓取完成')

        df = pd.DataFrame(rates_data)
        print(df)
        jpy_df = df[["日元"]]
        
        # 遍历抓取到的汇率数据，检查是否需要提醒
        for currency in rates_data.keys():
            if currency in CURRENCY_THRESHOLDS:
                threshold = CURRENCY_THRESHOLDS.get(currency)
                if float(rates_data[currency]['现汇买入价']) < threshold:
                    current_rate = rates_data[currency]['现汇买入价']
                    if currency == '澳大利亚元':
                        message = f'{currency}现汇买入价: {current_rate}, 低于{threshold}'
                        send_notification(title='汇率提醒', message=message)
                    if currency == '日元':
                        message = f'当前{currency}汇率低于{threshold}' + '\n' + jpy_df.to_string()
                        send_email(
                            subject='汇率提醒', 
                            body=message, 
                            sender=EMAIL_CONFIG['sender'],
                            password=EMAIL_CONFIG['password'],
                            receiver=EMAIL_CONFIG['receiver'],
                            smtp_server=EMAIL_CONFIG['smtp_server'],
                            smtp_port=EMAIL_CONFIG['smtp_port'])

    except Exception as e:
        print(f'出现错误：{e}')

if __name__ == '__main__':
    main()

