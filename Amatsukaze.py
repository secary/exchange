from amatsukaze.fetcher import get_exchange_rate
from amatsukaze.storage import store_data
from amatsukaze.notifier import send_notification, send_email
from config import WEBSITE,CURRENCIES, CURRENCY_THRESHOLDS, EMAIL_CONFIG
import pandas as pd

def send_alert(currency, current_rate, threshold, df):
    """
    发送通知和邮件提醒的通用函数
    """
    # 通知内容
    note = f"{currency}现汇买入价: {current_rate}, 低于 {threshold}"
    send_notification(title="汇率提醒", message=note)

    # 邮件正文
    message = (
        f"当前{currency}汇率低于{threshold}\n\n"
        f"以下是详细数据：\n{df[[currency]].to_string()}"
    )

    # 邮件接收者
    if currency == "日元":
        receivers = EMAIL_CONFIG['receiver']
    elif currency == "澳大利亚元":
        receivers = [EMAIL_CONFIG['receiver'][0]]
    else:
        receivers = []

    # 发送邮件（仅当有接收者时）
    if receivers:
        send_email(
            subject="汇率提醒",
            body=message,
            sender=EMAIL_CONFIG['sender'],
            password=EMAIL_CONFIG['password'],
            receivers=receivers,
            smtp_server=EMAIL_CONFIG['smtp_server'],
            smtp_port=EMAIL_CONFIG['smtp_port']
        )



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

        # 遍历汇率数据并检查是否需要提醒
        for currency, data in rates_data.items():
            if currency in CURRENCY_THRESHOLDS:
                threshold = CURRENCY_THRESHOLDS[currency]
                current_rate = float(data['现汇卖出价'])

                if current_rate <= threshold:
                    send_alert(currency, current_rate, threshold, df)

    except Exception as e:
        print(f"出现错误：{e}")

if __name__ == '__main__':
    main()
