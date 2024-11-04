import requests
from bs4 import BeautifulSoup
import json
import os

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f'下载图片失败，状态码: {response.status_code}')
            return False
    except Exception as e:
        print(f'下载图片时发生错误: {e}')
        return False

def get_steam_sales():
    url = 'https://store.steampowered.com/search/?specials=1&ndl=1'  # Steam特惠搜索页面URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有特惠游戏的元素
        game_elements = soup.find_all('a', class_='search_result_row')
        
        print(f"找到 {len(game_elements)} 个游戏元素")
        
        games = []
        for game in game_elements:
            # 检查是否存在 data-ds-appid 属性
            if 'data-ds-appid' in game.attrs:
                game_id = game['data-ds-appid']
                title = game.find('span', class_='title').text.strip()
                discount = game.find('div', class_='search_discount').text.strip() if game.find('div', class_='search_discount') else '无折扣'
                
                # 提取原价和折后价
                price_div = game.find('div', class_='search_price_discount_combined')
                if price_div:
                    original_price = price_div.find('div', class_='discount_original_price').text.strip() if price_div.find('div', class_='discount_original_price') else '无原价'
                    final_price = price_div.find('div', class_='discount_final_price').text.strip() if price_div.find('div', class_='discount_final_price') else '无折后价'
                else:
                    original_price = '无原价'
                    final_price = '无折后价'
                
                # 提取游戏的商店链接
                game_url = game['href']
                
                # 提取游戏的图片链接
                img_tag = game.find('img')
                img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
                
                if img_url:
                    # 下载图片并保存到本地
                    resources_dir = 'resources'
                    if not os.path.exists(resources_dir):
                        os.makedirs(resources_dir)
                    
                    img_filename = f"{game_id}.jpg"
                    local_img_path = os.path.join(resources_dir, img_filename)
                    
                    if download_image(img_url, local_img_path):
                        print(f"图片 {img_filename} 下载成功")
                    else:
                        print(f"图片 {img_filename} 下载失败")
                else:
                    local_img_path = None
                
                game_info = {
                    "title": title,
                    "url": game_url,
                    "img": img_url,
                    "id": game_id,
                    "local_img_path": local_img_path,
                    "original_price": original_price,
                    "final_price": final_price,
                    "discount": discount
                }
                games.append(game_info)
            else:
                print("未找到游戏ID，跳过此游戏")
                # 打印没有 game_id 的游戏元素的 HTML 代码，以便进一步调试
                print(game.prettify())
        
        # 将数据保存为JSON文件
        with open('steam_sales.json', 'w', encoding='utf-8') as f:
            json.dump(games, f, ensure_ascii=False, indent=4)
        
        print('数据已保存到 steam_sales.json 文件中')
    else:
        print(f'请求失败，状态码: {response.status_code}')

if __name__ == '__main__':
    get_steam_sales()