import requests
import json

# 替换为你的 Steam Web API 密钥
api_key = '2F8989788690680CADD3246A4B073805'

# 构建请求 URL
url = f'https://api.steampowered.com/ISteamApps/GetAppList/v2/?key={api_key}'

# 发送 HTTP GET 请求，显式禁用代理
try:
    response = requests.get(url, proxies={"http": None, "https": None})
    response.raise_for_status()  # 检查请求是否成功
except requests.RequestException as e:
    print(f"请求失败: {e}")
    exit()

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()
    
    # 打印原始数据，以便调试
    print(json.dumps(data, indent=4))
    
    # 解析 JSON 数据
    apps = data.get('applist', {}).get('apps', [])
    
    # 检查是否有数据
    if not apps:
        print("没有找到游戏数据")
        exit()
    
    # 将数据存储到文件中
    with open('games.json', 'w') as f:
        json.dump(apps, f, indent=4)
    print("数据已成功保存到 games.json")
else:
    print(f"请求失败，状态码: {response.status_code}")