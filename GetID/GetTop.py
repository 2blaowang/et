import requests
import json
import time

# 1. 使用 Steam 商店页面 API 获取热门游戏列表
def get_popular_games(max_retries=3, timeout=10):
    url = 'https://store.steampowered.com/api/featuredcategories'
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'specials' in data and 'items' in data['specials']:
                    return data['specials']['items']
                else:
                    raise Exception("Unexpected response format")
            else:
                raise Exception(f"Failed to fetch popular games: {response.status_code}")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2)  # 等待2秒后重试
            else:
                raise Exception(f"Max retries ({max_retries}) reached. Failed to fetch popular games.")

# 2. 保存热门游戏 ID 到文件
def save_popular_games_to_file(games, filename='popular_games.json'):
    with open(filename, 'w') as f:
        json.dump(games, f, indent=4)
    print(f"Saved {len(games)} popular games to {filename}")

def main():
    try:
        # 获取热门游戏
        popular_games = get_popular_games()
        # 保存热门游戏到文件
        save_popular_games_to_file(popular_games)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()