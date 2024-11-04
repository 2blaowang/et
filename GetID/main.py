import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QProgressBar, QGridLayout, QDialog, QTabWidget
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QEvent, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Steam API Key
STEAM_API_KEY = 'YOUR_STEAM_API_KEY'

class GameListWidget(QWidget):
    def __init__(self, title, data_file, parent=None):
        super().__init__(parent)
        self.title = title
        self.data_file = data_file
        self.initUI()
        self.load_games()

    def initUI(self):
        main_layout = QVBoxLayout()

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

    def load_games(self):
        # 从文件中读取游戏信息
        try:
            with open(self.data_file, 'r') as f:
                games = json.load(f)
            games = games[:10]  # 只取前10个游戏
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading games from {self.data_file}: {e}")
            return

        if not games:
            print(f"No valid games found in {self.data_file}")
            return

        self.game_list.clear()  # 清空当前列表

        # 显示长方形加载条
        self.loading_indicator.setValue(0)
        self.loading_indicator.setVisible(True)

        for game in games:
            self.add_game_to_list(game)

    def add_game_to_list(self, game_info):
        item = QListWidgetItem(self.game_list)
        widget = QWidget()
        layout = QGridLayout()

        # 添加游戏ID
        id_label = QLabel(f"游戏ID: {game_info['id']}")
        layout.addWidget(id_label, 0, 0)  # 放在第一列

        # 添加游戏名称
        name_label = QLabel(f"游戏名称: {game_info['name']}")
        name_label.setWordWrap(True)  # 允许自动换行
        name_label.setFixedWidth(200)  # 设置固定宽度
        layout.addWidget(name_label, 0, 1)  # 放在第二列

        # 添加游戏价格
        price_label = QLabel(f"游戏价格: {game_info.get('final_price', 'N/A')} {game_info.get('currency', 'N/A')}")
        layout.addWidget(price_label, 1, 1)  # 放在第二列的下面

        # 添加解锁按钮
        unlock_button = QPushButton('解锁')
        unlock_button.setProperty('app_id', game_info['id'])  # 提取 app_id
        unlock_button.clicked.connect(self.on_unlock_button_clicked)
        layout.addWidget(unlock_button, 0, 2, 2, 1)  # 将按钮放在第三列

        # 将游戏信息存储在标签中，以便后续使用
        id_label.setProperty('store_url', f"https://store.steampowered.com/app/{game_info['id']}")
        id_label.setCursor(QCursor(Qt.PointingHandCursor))  # 设置鼠标指针为手形

        # 为 QLabel 安装事件过滤器
        id_label.installEventFilter(self)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.game_list.setItemWidget(item, widget)

        # 打印 store_url 以确认是否正确设置
        print(f"Set store_url for app ID {game_info['id']}: {id_label.property('store_url')}")

        # 更新长方形加载条
        self.loading_indicator.setValue(int((self.game_list.count() / 10) * 100))
        print(f"Added game to list: {game_info['name']} (ID: {game_info['id']})")

    def hide_loading_indicator(self):
        self.loading_indicator.setVisible(False)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
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

class GameImageSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('游戏列表')
        self.setGeometry(100, 100, 1400, 800)

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 添加选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(GameListWidget("热门", "popular_games.json"), "热门")
        self.tab_widget.addTab(GameListWidget("最新", "new_games.json"), "最新")
        self.tab_widget.addTab(GameListWidget("其他", "other_games.json"), "其他")

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameImageSearchApp()
    ex.show()
    sys.exit(app.exec_())