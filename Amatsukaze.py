#!/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Filename : Amatsukaze
@Description : This is a Web Crawler to get Exchange Rate data from CNY to AUD and JPY, and store the data in local csv files.
@Datatime : 2024/10/14
@Author : Secary
@Version : Kai
'''

import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import pymysql

website = "https://www.boc.cn/sourcedb/whpj/"

def engine():
    sql = {
        'user': 'root',
        'password': '1519040104',
        'host': '172.20.43.197',
        'database': 'exchange'
        }
    return create_engine((f"mysql+pymysql://{sql['user']}:{sql['password']}@{sql['host']}/{sql['database']}"))

def askurl(url):
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")

    # Save the raw HTML to a file for debugging
    # with open('/home/mt/root/exchange/debug.html', 'w', encoding='utf-8') as file:
    #     file.write(html)
    
    return html

def getexchange_rate(url, currencies):
    html = askurl(url)  # 获取 HTML 内容
    soup = BeautifulSoup(html, "html.parser")
    
    data_list = []
    
    for currency in currencies:
        # 找到包含特定货币的 <td>
        target_td = soup.find('td', string=currency)  # 使用 string 替代 text
        if target_td:
            # 从目标 <td> 中获取父 <tr> 标签
            row = target_td.find_parent('tr')  # 获取父 <tr> 标签
            
            # 提取该行中所有 <td> 的文本
            result = [td.get_text(strip=True) for td in row.find_all('td')]
            data_list.append(result)  # 将结果添加到列表中
        else:
            print(f"未找到包含'{currency}'的<td>标签")
    
    return data_list  # 返回包含所有货币数据的列表

def store_data(datalist, csv_file="/home/mt/root/exchange/data/ExchangeRates.csv"):
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
    


    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_updated = df_new

    try:
        df_updated.to_csv(csv_file, index=False)
        print(f'数据成功存储到{csv_file}')
        df_updated.to_sql('rates', con=engine(), if_exists='replace', index=False)
        print(f'数据成功存储到exchange.rates')
    except OperationalError as e:
        print(f"数据库操作错误: {e.orig}.")
        if "Can't connect to MySQL server" in str(e.orig):
            print("请检查MySQL服务器是否在正确的地址运行")


def main():
    try:
        currencies = ["澳大利亚元", "日元"]  # 可变的货币列表
        print(f'开始抓取人民币兑换{"、".join(currencies)}汇率数据')
        rates_data = getexchange_rate(website, currencies)
        store_data(rates_data)
        print('汇率数据抓取完成')
    except Exception as e:
        print('出现错误： ', e)
    
if __name__ == '__main__':
    main()



   