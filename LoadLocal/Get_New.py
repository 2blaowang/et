import os
import json
import requests
from bs4 import BeautifulSoup
import re

# Steam新游页面URL
STEAM_NEW_RELEASES_URL = "https://store.steampowered.com/explore/new/"

# 资源文件夹路径
RESOURCES_DIR = "resources"

# 新游戏数据文件路径
NEW_GAMES_JSON_PATH = "New_Games.json"

# 最大重试次数
MAX_RETRIES = 3

# Steam图片URL模板
STEAM_IMAGE_URL_TEMPLATE = "https://cdn.akamai.steamstatic.com/steam/apps/{}/header.jpg"

def fetch_new_games():
    # 创建资源文件夹
    if not os.path.exists(RESOURCES_DIR):
        os.makedirs(RESOURCES_DIR)

    # 发送HTTP请求获取页面内容
    response = requests.get(STEAM_NEW_RELEASES_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from Steam")

    soup = BeautifulSoup(response.content, 'html.parser')
    new_games = []

    # 查找新游卡片
    game_cards = soup.find_all('a', class_='tab_item')
    for card in game_cards:
        title = card.find('div', class_='tab_item_name').text.strip()
        url = card['href']
        app_id = re.search(r'/app/(\d+)/', url).group(1)  # 从URL中提取游戏ID

        # 获取价格信息
        price_div = card.find('div', class_='discount_final_price')
        if price_div:
            final_price = price_div.text.strip()
            original_price_div = card.find('div', class_='discount_original_price')
            original_price = original_price_div.text.strip() if original_price_div else final_price
            discount = card.find('div', class_='discount_percent').text.strip() if card.find('div', class_='discount_percent') else '无折扣'
        else:
            final_price = 'Free to Play'
            original_price = 'Free to Play'
            discount = '无折扣'

        # 构建图片URL
        img_url = STEAM_IMAGE_URL_TEMPLATE.format(app_id)

        # 获取游戏图片
        img_filename = os.path.join(RESOURCES_DIR, f"{app_id}.jpg")  # 使用游戏ID作为文件名
        img_downloaded = False
        for attempt in range(MAX_RETRIES):
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open(img_filename, 'wb') as img_file:
                    img_file.write(img_response.content)
                img_downloaded = True
                break
            else:
                print(f"尝试 {attempt + 1}/{MAX_RETRIES} 下载图片失败，状态码: {img_response.status_code}")
        
        if not img_downloaded:
            img_filename = None

        new_games.append({
            "title": title,
            "url": url,
            "img": img_url,
            "id": app_id,
            "local_img_path": img_filename,
            "original_price": original_price,
            "final_price": final_price,
            "discount": discount
        })

    # 保存新游戏数据到JSON文件
    with open(NEW_GAMES_JSON_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(new_games, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_new_games()