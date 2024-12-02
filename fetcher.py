import urllib.request
import urllib.error
from bs4 import BeautifulSoup

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
    return html

def get_exchange_rate(url, currencies):
    html = askurl(url)
    soup = BeautifulSoup(html, "html.parser")
    
    data_list = []
    for currency in currencies:
        target_td = soup.find('td', string=currency)
        if target_td:
            row = target_td.find_parent('tr')
            result = [td.get_text(strip=True) for td in row.find_all('td')]
            data_list.append(result)
        else:
            print(f"未找到包含'{currency}'的<td>标签")
    return data_list
