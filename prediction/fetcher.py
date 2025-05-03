import urllib.request
import urllib.error
from bs4 import BeautifulSoup

def askurl(url):
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=head)
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        return html
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return ""

def get_exchange_rate(url, currencies):
    if not isinstance(currencies, list):
        raise ValueError("currencies 参数必须是一个列表")
    
    html = askurl(url)
    if not html:
        print("未能获取 HTML 内容")
        return {}
    
    soup = BeautifulSoup(html, "html.parser")
    result = {}
    
    for currency in currencies:
        target_td = soup.find('td', string=currency)
        if target_td:
            row = target_td.find_parent('tr')
            row_data = [td.get_text(strip=True) for td in row.find_all('td')]
            result[row_data[0]] = {
                "现汇卖出价": row_data[3],
                "日期": row_data[6]
            }
        else:
            print(f"未找到包含'{currency}'的<td>标签")
    return result
