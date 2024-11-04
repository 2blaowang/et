import sys
import random
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QGridLayout, QProgressBar, QMainWindow, QDialog, QVBoxLayout
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal, QTimer, QEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView  # 正确的导入
import json
import time

class GameLoaderThread(QThread):
    game_loaded = pyqtSignal(dict)
    loading_failed = pyqtSignal(str)

    def __init__(self, app_ids, all_app_ids, parent=None):
        super().__init__(parent)
        self.app_ids = app_ids
        self.all_app_ids = all_app_ids

    def run(self):
        loaded_count = 0
        while loaded_count < 8 and self.app_ids:
            app_id = self.app_ids.pop(0)
            game_info = self.get_game_info(app_id)
            if game_info:
                self.game_loaded.emit(game_info)
                loaded_count += 1
            else:
                self.loading_failed.emit(app_id)
                # 如果加载失败，重新随机选择一个新的游戏 ID
                new_app_id = random.choice(self.all_app_ids)
                while new_app_id in self.app_ids:
                    new_app_id = random.choice(self.all_app_ids)
                self.app_ids.append(new_app_id)
            time.sleep(1)  # 添加延迟以避免请求过快

    def get_game_info(self, app_id):
        url = f"https://store.steampowered.com/app/{app_id}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # 检查响应状态码
            soup = BeautifulSoup(response.text, 'html.parser')
            
            img_tag = soup.find('img', {'class': 'game_header_image_full'})
            name_tag = soup.find('div', {'class': 'apphub_AppName'})
            price_tag = soup.find('div', {'class': 'game_purchase_price'})

            if img_tag and name_tag and price_tag:
                return {
                    'image_url': img_tag['src'],
                    'name': name_tag.text.strip(),
                    'price': price_tag.text.strip(),
                    'store_url': url,
                    'appid': app_id  # 添加游戏ID
                }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game info for app ID {app_id}: {e}")
        return None

class GameImageSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Steam 游戏图片搜索')
        self.setGeometry(100, 100, 1400, 800)

        self.initUI()
        self.load_random_games()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 添加“换一波”按钮
        self.refresh_button = QPushButton('换一波')
        self.refresh_button.clicked.connect(self.load_random_games)
        main_layout.addWidget(self.refresh_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        # 添加游戏列表
        self.game_list = QListWidget()
        self.game_list.viewport().installEventFilter(self)  # 安装事件过滤器
        main_layout.addWidget(self.game_list)

        # 添加长方形加载条
        self.loading_indicator = QProgressBar(self)
        self.loading_indicator.setAlignment(Qt.AlignCenter)
        self.loading_indicator.setRange(0, 100)
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #8A2BE2;  /* 草紫色 */
            }
        """)

        # 调整布局，将长方形加载条放在右下角
        main_layout.addWidget(self.loading_indicator, alignment=Qt.AlignBottom | Qt.AlignRight)

        self.setLayout(main_layout)

    def load_random_games(self):
        # 从文件中读取所有游戏 ID
        with open('steam_games.json', 'r') as f:
            all_games = json.load(f)
        all_app_ids = [str(game['appid']) for game in all_games]

        # 随机选择8个游戏 ID
        random_app_ids = random.sample(all_app_ids, 8)
        self.game_list.clear()  # 清空当前列表

        # 显示长方形加载条
        self.loading_indicator.setValue(0)
        self.loading_indicator.setVisible(True)

        # 启动加载线程
        self.loader_thread = GameLoaderThread(random_app_ids, all_app_ids)
        self.loader_thread.game_loaded.connect(self.add_game_to_list)
        self.loader_thread.loading_failed.connect(self.handle_loading_failure)
        self.loader_thread.finished.connect(self.hide_loading_indicator)
        self.loader_thread.start()

    def add_game_to_list(self, game_info):
        item = QListWidgetItem(self.game_list)
        widget = QWidget()
        layout = QGridLayout()

        # 添加游戏图片
        image_label = QLabel()
        response = requests.get(game_info['image_url'], timeout=30)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            image_label.setPixmap(pixmap.scaledToWidth(100, Qt.SmoothTransformation))
        layout.addWidget(image_label, 0, 0, 2, 1)

        # 添加游戏ID
        id_label = QLabel(f"游戏ID: {game_info['appid']}")
        layout.addWidget(id_label, 0, 1)  # 放在游戏图片的右边

        # 添加游戏名称
        name_label = QLabel(f"游戏名称: {game_info['name']}")
        name_label.setWordWrap(True)  # 允许自动换行
        name_label.setFixedWidth(200)  # 设置固定宽度
        layout.addWidget(name_label, 0, 2)  # 放在游戏ID的右边

        # 添加游戏价格
        price_label = QLabel(f"游戏价格: {game_info['price']}")
        layout.addWidget(price_label, 1, 2)  # 放在游戏名称的下面

        # 添加解锁按钮
        unlock_button = QPushButton('解锁')
        unlock_button.setProperty('app_id', game_info['appid'])  # 提取 app_id
        unlock_button.clicked.connect(self.on_unlock_button_clicked)
        layout.addWidget(unlock_button, 0, 3, 2, 1)  # 将按钮放在最右边

        # 将游戏信息存储在标签中，以便后续使用
        image_label.setProperty('store_url', game_info['store_url'])
        image_label.setCursor(QCursor(Qt.PointingHandCursor))  # 设置鼠标指针为手形

        # 为 QLabel 安装事件过滤器
        image_label.installEventFilter(self)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.game_list.setItemWidget(item, widget)

        # 更新长方形加载条
        self.loading_indicator.setValue(int((self.game_list.count() / 8) * 100))

    def handle_loading_failure(self, app_id):
        print(f"Failed to load game info for app ID {app_id}")

    def hide_loading_indicator(self):
        self.loading_indicator.setVisible(False)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            print(f"EventFilter detected a MouseButtonPress event on object: {obj}")
            if isinstance(obj, QLabel):
                store_url = obj.property('store_url')
                if store_url:
                    print(f"Mouse click detected on label with URL: {store_url}")  # 调试信息
                    self.open_web_view(store_url)
        return super().eventFilter(obj, event)

    def open_web_view(self, url):
        print(f"Opening URL: {url}")  # 调试信息
        web_view = QWebEngineView()
        web_view.loadFinished.connect(lambda ok: self.on_load_finished(ok, url))
        web_view.setUrl(QUrl(url))

        # 使用 QDialog 替代 QMainWindow
        web_dialog = QDialog(self)
        web_dialog.setWindowTitle('Steam 商店页面')
        web_dialog_layout = QVBoxLayout()
        web_dialog_layout.addWidget(web_view)
        web_dialog.setLayout(web_dialog_layout)
        web_dialog.resize(800, 600)
        web_dialog.exec_()  # 使用 exec_() 使对话框模态

    def on_load_finished(self, ok, url):
        if not ok:
            print(f"Failed to load URL: {url}")
        else:
            print(f"Successfully loaded URL: {url}")

    def on_unlock_button_clicked(self):
        button = self.sender()
        app_id = button.property('app_id')
        print(f"解锁按钮被点击，游戏 ID: {app_id}")

        # 这里可以添加更多的逻辑，比如发送请求到服务器等
        # 例如：调用某个 API 来解锁游戏
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameImageSearchApp()
    ex.show()
    sys.exit(app.exec_())