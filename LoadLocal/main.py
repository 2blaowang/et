import sys
import json
import os
import random
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QListWidget, QListWidgetItem, QLabel, QGridLayout, QWidget, QVBoxLayout, QDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QUrl
from Login import scrape_steam_data
from PyQt5.QtWebEngineWidgets import QWebEngineView  # 导入 QWebEngineView
from webdriver_manager.chrome import ChromeDriverManager

class ClickableLabel(QLabel):
    def __init__(self, url, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.main_window = main_window

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isEnabled():
            self.main_window.open_game_page(self.url)

class ProfilePictureLabel(ClickableLabel):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(None, main_window, *args, **kwargs)
        self.setEnabled(True)  # 默认启用点击事件

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isEnabled():
            self.main_window.show_login_dialog()

class GameListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steam Games List")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 添加圆形头像
        self.add_profile_picture(main_layout)
        
        # 创建QTabWidget
        self.tab_widget = QTabWidget()
        
        # 创建“热门”、“最新”和“特惠”选项卡
        self.popular_tab = QListWidget()
        self.new_tab = QListWidget()
        self.discount_tab = QListWidget()
        
        # 设置QListWidget的大小模式
        self.popular_tab.setResizeMode(QListWidget.Adjust)
        self.new_tab.setResizeMode(QListWidget.Adjust)
        self.discount_tab.setResizeMode(QListWidget.Adjust)
        
        self.tab_widget.addTab(self.popular_tab, "热门")
        self.tab_widget.addTab(self.new_tab, "最新")
        self.tab_widget.addTab(self.discount_tab, "特惠")
        
        # 将QTabWidget添加到主布局
        main_layout.addWidget(self.tab_widget)
        
        # 创建中心部件并设置布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 加载游戏数据
        self.load_games_data()

    def add_profile_picture(self, layout):
        # 创建一个头像的 QLabel
        self.profile_picture = ProfilePictureLabel(self, parent=self)  # 传递主窗口实例
        self.profile_picture.setFixedSize(80, 80)  # 固定大小
        self.profile_picture.setAlignment(Qt.AlignCenter)
        
        # 默认显示 Default.jpg
        default_image_path = os.path.join("User", "Default.jpg")
        if os.path.exists(default_image_path):
            self.load_profile_picture(default_image_path)
        else:
            self.profile_picture.setText("P")
        
        # 将头像添加到布局
        layout.addWidget(self.profile_picture, alignment=Qt.AlignRight | Qt.AlignTop)

    def load_profile_picture(self, file_path):
        if os.path.exists(file_path):
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_picture.setPixmap(scaled_pixmap)
        else:
            self.profile_picture.setText("P")

    def update_profile_picture(self, file_path):
        if os.path.exists(file_path):
            self.load_profile_picture(file_path)
        else:
            self.profile_picture.setText("P")

    def load_games_data(self):
        # 加载热门游戏数据
        self.load_games_to_list(self.popular_tab, 'steam_games.json')
        
        # 加载最新游戏数据
        self.load_games_to_list(self.new_tab, 'New_Games.json')
        
        # 加载特惠游戏数据
        self.load_games_to_list(self.discount_tab, 'steam_sales.json')

    def load_games_to_list(self, list_widget, file_path):
        list_widget.clear()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                games = json.load(f)
            
            for game in games:
                item = QListWidgetItem(list_widget)
                widget = QWidget()
                grid_layout = QGridLayout()  # 使用网格布局
                
                # 创建图片标签
                img_label = ClickableLabel(game.get('url', ''), self)  # 传递主窗口实例
                if os.path.exists(game.get('local_img_path', '')):
                    pixmap = QPixmap(game['local_img_path'])
                    img_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    img_label.setText("No Image Available")
                img_label.setAlignment(Qt.AlignTop)  # 图片顶部对齐
                grid_layout.addWidget(img_label, 0, 0, 2, 1)  # 占据两行一列
                
                # 创建信息标签
                title_label = QLabel(f"<b>{game.get('title', 'Unknown')}</b>")
                title_label.setAlignment(Qt.AlignTop)
                grid_layout.addWidget(title_label, 0, 1, 1, 1)  # 占据一行一列
                
                original_price = game.get('original_price', 'N/A')
                final_price = game.get('final_price', 'N/A')
                price_label = QLabel(f"Original Price: {original_price}<br>Final Price: {final_price}")
                price_label.setAlignment(Qt.AlignTop)
                grid_layout.addWidget(price_label, 1, 1, 1, 1)  # 占据一行一列
                
                # 创建解锁按钮
                unlock_button = QPushButton("解锁")
                unlock_button.clicked.connect(lambda _, g=game: self.unlock_game(g))
                grid_layout.addWidget(unlock_button, 0, 2, 2, 1)  # 占据两行一列
                
                # 设置布局
                widget.setLayout(grid_layout)
                item.setSizeHint(widget.sizeHint())
                list_widget.addItem(item)
                list_widget.setItemWidget(item, widget)
    
        except FileNotFoundError:
            print(f"{file_path} 文件未找到")
        except json.JSONDecodeError:
            print(f"{file_path} 文件格式错误")

    # 新增的解锁游戏方法
    def unlock_game(self, game):
        print(f"解锁游戏: {game['title']}")
        # 在这里添加解锁游戏的逻辑

    def open_game_page(self, url):
        # 创建一个新的对话框窗口
        dialog = QDialog(self)
        dialog.setWindowTitle("Game Page")
        dialog.setGeometry(300, 200, 600, 320)
        
        # 创建QWebEngineView控件
        web_view = QWebEngineView(dialog)
        web_view.load(QUrl(url))
        
        # 设置布局
        layout = QVBoxLayout(dialog)
        layout.addWidget(web_view)
        
        dialog.setLayout(layout)
        dialog.show()

    def show_login_dialog(self):
        user_data = scrape_steam_data()
        if user_data:
            # 检查 User 文件夹中的图片并更新头像
            profile_image_path = os.path.join("User", "profile.jpg")
            if os.path.exists(profile_image_path):
                self.load_profile_picture(profile_image_path)
                print("头像已更新")
                self.profile_picture.setEnabled(False)  # 登录成功后禁用点击事件
            else:
                print("头像未找到")
        else:
            print("登录失败")
            self.profile_picture.setEnabled(True)  # 登录失败后重新启用点击事件

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameListWindow()
    window.show()
   
    window.resize(1024, 600)
    sys.exit(app.exec_())