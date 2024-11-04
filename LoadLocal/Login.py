import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
import time
import json

def get_steam_id_from_url(url):
    # 从URL中提取Steam ID
    return url.split('/')[-1]

def get_steam_api_key(driver):
    # 导航到获取API密钥的页面
    driver.get('https://steamcommunity.com/dev/apikey')

    # 等待页面加载完成
    time.sleep(5)

    # 查找包含 "密钥: " 的元素
    api_key_element = driver.find_elements(By.XPATH, "//p[contains(text(), '密钥: ')]")
    if api_key_element:
        # 提取密钥值
        api_key_text = api_key_element[0].text
        api_key = api_key_text.split('密钥: ')[1].strip()
        return api_key
    else:
        # 如果没有API密钥，提示用户创建
        print("没有找到API密钥，请手动创建API密钥。")
        input("请手动创建API密钥后按回车继续...")
        return get_steam_api_key(driver)

def get_steam_games(steam_id, api_key):
    # 构建Steam API URL
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=1&format=json"

    # 发送HTTP请求
    response = requests.get(url)
    
    # 检查请求是否成功
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return None

    # 解析JSON响应
    data = response.json()
    if 'response' in data and 'games' in data['response']:
        games = data['response']['games']
        return games
    else:
        print("无法获取游戏列表")
        return None

def save_to_json(data, filename='user_data.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

def scrape_steam_data():
    # 设置WebDriver路径
    service = Service(EdgeChromiumDriverManager().install())
    
    # 创建WebDriver选项
    options = webdriver.EdgeOptions()
    options.add_argument('--start-maximized')  # 最大化窗口以便用户操作

    # 创建WebDriver对象
    driver = webdriver.Edge(service=service, options=options)

    try:
        # 加载登录页面
        driver.get('https://steamcommunity.com/login/home/?goto=')

        # 等待用户手动完成登录
        print("请在浏览器中手动完成登录过程...")

        # 等待登录成功
        wait = WebDriverWait(driver, 60)  # 设置等待时间为60秒
        profile_page = wait.until(EC.url_contains('https://steamcommunity.com/profiles/'))
        
        # 获取登录后的URL
        current_url = driver.current_url
        print(f"登录成功，当前URL: {current_url}")

        # 从URL中提取Steam ID
        steam_id = get_steam_id_from_url(current_url)
        print(f"Steam ID: {steam_id}")

        # 获取API密钥
        api_key = get_steam_api_key(driver)
        if api_key:
            print(f"API密钥: {api_key}")
            with open('steam_api_key.txt', 'w') as file:
                file.write(api_key)
        else:
            print("无法获取API密钥，请检查是否已创建API密钥。")
            return None

        # 获取游戏列表
        games = get_steam_games(steam_id, api_key)
        
        if games:
            print(f"账号 {steam_id} 拥有的游戏列表:")
            for game in games:
                print(f"游戏名称: {game['name']}, 游戏ID: {game['appid']}")

            # 构建用户数据字典
            user_data = {
                "steam_id": steam_id,
                "api_key": api_key,
                "games": games
            }

            # 保存数据到JSON文件
            save_to_json(user_data)

            # 返回用户数据
            return user_data
        else:
            print("无法获取游戏列表，请检查Steam ID和API密钥是否正确。")
            return None

    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == '__main__':
    user_data = scrape_steam_data()
    if user_data:
        print("数据抓取成功！")
    else:
        print("数据抓取失败。")