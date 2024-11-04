import atexit
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

class SteamScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        atexit.register(self.quit_driver)

    def setup_driver(self):
        # 设置WebDriver路径
        service = Service(EdgeChromiumDriverManager().install())
        
        # 创建WebDriver选项
        options = webdriver.EdgeOptions()
        options.add_argument('--start-maximized')  # 最大化窗口以便用户操作

        # 创建WebDriver对象
        self.driver = webdriver.Edge(service=service, options=options)

    def scrape_steam_data(self, username, password):
        try:
            # 加载登录页面
            self.driver.get('https://steamcommunity.com/login/home/?goto=')

            # 等待页面加载完成
            wait = WebDriverWait(self.driver, 60)

            # 定位账号和密码输入框
            username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @class="_2GBWeup5cttgbTw8FM3tfx"]')))
            password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password" and @class="_2GBWeup5cttgbTw8FM3tfx"]')))

            # 输入账号和密码
            username_input.send_keys(username)
            password_input.send_keys(password)

            # 定位并点击登录按钮
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
            login_button.click()

            # 等待登录成功
            profile_page = wait.until(EC.url_contains('https://steamcommunity.com/profiles/'))
            
            # 获取登录后的URL
            current_url = self.driver.current_url
            print(f"登录成功，当前URL: {current_url}")

            # 从URL中提取Steam ID
            steam_id = self.get_steam_id_from_url(current_url)
            print(f"Steam ID: {steam_id}")

            # 转到指定的游戏页面
            game_url = 'https://store.steampowered.com/app/48000/LIMBO/'
            self.driver.get(game_url)

            # 等待页面加载完成
            time.sleep(5)

            # 打印当前URL以确认已转到指定的游戏页面
            print(f"已转到指定的游戏页面，当前URL: {self.driver.current_url}")

            # 找到并点击“添加至购物车”按钮
            add_to_cart_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@id="btn_add_to_cart_11010"]')))
            add_to_cart_button.click()

            # 等待页面加载完成
            time.sleep(5)

            # 打印当前URL以确认已添加到购物车
            print(f"已添加到购物车，当前URL: {self.driver.current_url}")

            # 直接跳转到购物车页面
            cart_url = 'https://store.steampowered.com/cart'
            self.driver.get(cart_url)

            # 等待购物车页面加载完成
            wait.until(EC.url_to_be(cart_url))

            # 打印当前URL以确认已查看购物车
            print(f"已查看购物车，当前URL: {self.driver.current_url}")

            # 检查当前地区是否为美国
            current_region = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="DialogDropDown_CurrentDisplay"]'))).text
            print(f"当前地区: {current_region}")

            if "美国 ( $ )" not in current_region:
                # 执行切换国家的JavaScript代码
                change_country_script = """
                function changeCountryToUS() {
                    if (!window.$CurrencyChangeDialog) {
                        window.$CurrencyChangeDialog = $J('#currency_change_confirm_dialog');
                    }

                    var $Dialog = window.$CurrencyChangeDialog;
                    $Dialog.children('.currency_have_options').hide();
                    $Dialog.children('.currency_no_options').hide();

                    var WaitModal = ShowBlockingWaitDialog('正在更改国家/地区…', '');
                    CrossDomainPost('https://store.steampowered.com/country/setcountry', { sessionid: g_sessionID, cc: 'US' }).done(function () {
                        CrossDomainPost('https://checkout.steampowered.com/country/setcountry', { sessionid: g_sessionID, cc: 'US' }).done(function () {
                            WaitModal.Dismiss();
                            window.location = 'https://store.steampowered.com/cart/';
                        }).fail(function () {
                            WaitModal.Dismiss();
                            ShowAlertDialog('更改国家/地区', '更改您的国家/地区时遇到问题。请稍后再试。');
                        });
                    }).fail(function () {
                        WaitModal.Dismiss();
                        ShowAlertDialog('更改国家/地区', '更改您的国家/地区时遇到问题。请稍后再试。');
                    });
                }

                // 调用切换国家的函数
                changeCountryToUS();
                """

                # 执行JavaScript代码
                self.driver.execute_script(change_country_script)

                # 等待页面加载完成
                time.sleep(10)

                # 重新检查当前地区
                current_region = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="DialogDropDown_CurrentDisplay"]'))).text
                print(f"当前地区: {current_region}")

            # 直接跳转到目标游戏页面
            target_game_url = 'https://store.steampowered.com/app/1059550/Valve_Index/'
            self.driver.get(target_game_url)
            print(f"已跳转到目标游戏页面，当前URL: {self.driver.current_url}")

            # 找到并点击“添加至购物车”按钮
            add_to_cart_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="btn_green_steamui btn_medium" and contains(@href, "javascript:addToCart(354234)")]')))
            add_to_cart_button.click()

            # 等待页面加载完成
            time.sleep(5)

            # 打印当前URL以确认已添加目标游戏到购物车
            print(f"已添加目标游戏到购物车，当前URL: {self.driver.current_url}")

            # 跳转到购物车页面
            cart_url = 'https://store.steampowered.com/cart'
            self.driver.get(cart_url)

            # 等待购物车页面加载完成
            wait.until(EC.url_to_be(cart_url))

            # 打印当前URL以确认已查看购物车
            print(f"已查看购物车，当前URL: {self.driver.current_url}")

            # 停止进一步操作，等待用户手动关闭浏览器
            input("按Enter键关闭浏览器...")

        except Exception as e:
            print(f"发生错误: {e}")
            input("按Enter键关闭浏览器...")

    def get_steam_id_from_url(self, url):
        # 从URL中提取Steam ID
        return url.split('/')[-1]

    def quit_driver(self):
        if self.driver:
            self.driver.quit()

# if __name__ == '__main__':
#     # 测试代码
#     scraper = SteamScraper()
#     username = '1783713'
#     password = 'Yz17340520358,'
#     scraper.scrape_steam_data(username, password)