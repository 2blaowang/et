import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse

# 创建资源目录
RESOURCES_DIR = 'resources'
os.makedirs(RESOURCES_DIR, exist_ok=True)

def fetch_games_from_search_page():
    base_url = "https://store.steampowered.com/search/"
    params = {
        'page': 1
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    game_blocks = soup.find_all('a', class_='search_result_row')
    
    games = []
    
    for block in game_blocks:
        game_id = extract_game_id(block['href'])
        game = {
            'title': block.find('span', class_='title').text.strip() if block.find('span', class_='title') else 'No title available',
            'url': block['href'],
            'img': block.find('img')['src'] if block.find('img') else 'No image available',
            'id': game_id,
            'local_img_path': download_image(block.find('img')['src'], game_id) if block.find('img') else 'No image available'
        }
        price_info = fetch_game_price(game_id)
        game.update(price_info)
        games.append(game)
    
    return games

def extract_game_id(url):
    # 使用正则表达式从URL中提取游戏ID
    match = re.search(r'app/(\d+)', url)
    if match:
        return match.group(1)
    return 'No ID available'

def fetch_game_price(game_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return {
            'original_price': 'No price available',
            'final_price': 'No price available',
            'discount': '无折扣'
        }
    
    data = response.json()
    if data.get(game_id, {}).get('success', False):
        price_overview = data[game_id]['data'].get('price_overview', {})
        if price_overview:
            original_price = price_overview.get('initial_formatted', '')
            final_price = price_overview.get('final_formatted', 'No price available')
            if not original_price:
                original_price = final_price
            discount = f"{price_overview.get('discount_percent', 0)}%" if price_overview.get('discount_percent', 0) > 0 else '无折扣'
            return {
                'original_price': original_price,
                'final_price': final_price,
                'discount': discount
            }
        else:
            return {
                'original_price': 'Free to Play',
                'final_price': 'Free to Play',
                'discount': '无折扣'
            }
    return {
        'original_price': 'No price available',
        'final_price': 'No price available',
        'discount': '无折扣'
    }

def download_image(img_url, game_id):
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            img_extension = os.path.splitext(urlparse(img_url).path)[1]
            img_name = f"{game_id}{img_extension}"
            img_path = os.path.join(RESOURCES_DIR, img_name)
            with open(img_path, 'wb') as f:
                f.write(response.content)
            return img_path
        else:
            print(f"下载图片失败，状态码: {response.status_code}")
            return 'No image available'
    except Exception as e:
        print(f"下载图片时发生错误: {e}")
        return 'No image available'

def save_to_json(data, filename='steam_games.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存至 {filename}")

if __name__ == "__main__":
    games = fetch_games_from_search_page()
    save_to_json(games)