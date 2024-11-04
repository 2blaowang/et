import requests
import json
import time

# 1. 注册 Steam Web API 密钥
STEAM_API_KEY = '2F8989788690680CADD3246A4B073805'

# 2. 使用 API 获取游戏列表
def get_all_apps(max_retries=3, timeout=10):
    url = f'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                return data['applist']['apps']
            else:
                raise Exception(f"Failed to fetch app list: {response.status_code}")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2)  # 等待2秒后重试
            else:
                raise Exception(f"Max retries ({max_retries}) reached. Failed to fetch app list.")

# 3. 保存游戏 ID 到文件
def save_apps_to_file(apps, filename='steam_games.json'):
    with open(filename, 'w') as f:
        json.dump(apps, f, indent=4)
    print(f"Saved {len(apps)} apps to {filename}")

def main():
    try:
        # 获取所有应用
        apps = get_all_apps()
        # 保存所有应用到文件
        save_apps_to_file(apps)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()