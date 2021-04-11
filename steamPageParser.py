import requests
import re
import json
import urllib
import urllib.request
from bs4 import BeautifulSoup

def itemId(url: str):
    # поиск id

    try:
        page = requests.get(url)
        result = re.findall(r'Market_LoadOrderSpread\(\s*(\d+)\s*\)', str(page.content))
        print(result)
        return result[0]
    except:
        return "Error" # неправильный url в запросе


def jsonReceiver(itemId):
    jsonUrl = f'https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={itemId}&two_factor=0'
    pageContent = urllib.request.urlopen(jsonUrl)
    data = json.loads(pageContent.read().decode())
    filename_first = data['sell_order_table']
    soup = BeautifulSoup(filename_first, 'html.parser')
    prof_divs = soup.select('table.market_commodity_orders_table')

    for td in prof_divs:
        headers_name = td.select('td')
        current_price = headers_name[0].text
    #for i in headers_name:
        #print(headers_name[i].select_one('td'))
    return current_price


def itemName(url: str):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        parse = soup.select('div.market_listing_nav')
        for i in parse:
            itemName = i.select('a')[1].text
        return itemName
    except:
        return "Error" # неправильный url в запросе

def getImgUrl(url: str, filename: str):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    parse = soup.select('div.market_listing_largeimage')
    for i in parse:
        itemImgUrl = str(i.select('img')[0])
        pattern = '''https://.*\"'''
        url = re.findall(f"{pattern}", itemImgUrl)[0][:-1]

    with open(f'imgs\{filename}', 'wb') as handle:
        response = requests.get(url, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

#print(jsonReceiver(itemId('https://steamcommunity.com/market/listings/730/Operation%20Broken%20Fang%20Case')))
#print(itemId('https://www.google.com/search?q=dgfdfg&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjR28CRg_zuAhVj_SoKHYdHAwIQ_AUoAXoECA8QAw&biw=1920&bih=937'))
#getImgUrl('https://steamcommunity.com/market/listings/730/Operation%20Broken%20Fang%20Case', '1.jpg')