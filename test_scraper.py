import time
import random
from fake_useragent import UserAgent 
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


ua = UserAgent()

headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

product = input("input the name of the product: ")

products = []

retry_count = 0

for i in range(1,8):

    url = f"https://www.amazon.in/s?k={product.strip().replace(" ","+")}&page={i}"
    response = requests.get(url,headers=headers)
    print("url: ",url)
    while response.status_code == 503 and retry_count < 5: 
        print("Something went wrong.. Forbidden status code!")
        time.sleep(retry_count*5+1)
        headers['User-Agent'] =  ua.random
        print("Retrying...")
        response = requests.get(url,headers=headers)
        retry_count += 1
        time.sleep(1)
    
    if retry_count > 5:
        print(f"Extraction of all pages failed.. \n Only extracted {i} pages")
        break
    time.sleep(random.uniform(2, 5))
    soup = BeautifulSoup(response.content,"html.parser")
    for item in soup.select('[data-component-type="s-search-result"]'):
        product_data = {
            'name': item.select_one('h2 span').text.strip() if item.select_one('h2 span') else None,
            'price': item.select_one('.a-price-whole').text.strip() if item.select_one('.a-price-whole') else None,
            'mrp': item.select_one('.a-text-price .a-offscreen').text.strip() if item.select_one('.a-text-price .a-offscreen') else None,
            'rating': item.select_one('span.a-icon-alt').text.strip() if item.select_one('span.a-icon-alt') else None,
            'url': 'https://amazon.in' + item.select_one('a.a-link-normal')['href'] if item.select_one('a.a-link-normal') else None,
        }
        products.append(product_data)
    print("Waiting for next page....")
    time.sleep(2)

if len(products) > 0:
    df = pd.json_normalize(products)
    df = df.drop_duplicates(subset=["name"])

    # Write the DataFrame to a CSV file
    df.to_csv(f"output_{product}.csv", index=False, encoding='utf-8')