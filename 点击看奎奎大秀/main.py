import sys
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QLabel, QPushButton, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QEvent
import requests

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("直播播放器")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D2D;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QListWidget {
                background-color: #3C3F41;
                color: white;
                border: 1px solid #4A4A4A;
                selection-background-color: #6A6C6E;
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
            QGraphicsView {
                background-color: black;
            }
        """)

        # 创建主窗口部件
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # 创建布局
        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        # 创建视频显示区域
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        layout.addWidget(self.graphics_view)

        # 创建播放列表
        self.playlist_label = QLabel("播放列表", self)
        layout.addWidget(self.playlist_label)

        self.playlist = QListWidget(self)
        layout.addWidget(self.playlist)

        # 加载播放列表
        self.load_playlist('http://adultiptv.net/lists/all.m3u')

        # 创建播放按钮
        self.play_button = QPushButton("播放", self)
        self.play_button.clicked.connect(self.play_selected_item)
        layout.addWidget(self.play_button)

        # 创建 VLC 实例
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        # 绑定键盘事件
        self.playlist.installEventFilter(self)

    def load_playlist(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            lines = response.text.splitlines()
            self.playlist.clear()
            title = None  # 初始化 title 变量

            for line in lines:
                if line.startswith('#EXTINF:'):
                    title = line.split(',')[1].strip()  # 获取标题并去除前后空格
                elif line and not line.startswith('#'):
                    if title is not None:
                        self.playlist.addItem(f"{title} - {line}")
                        title = None  # 重置 title 变量

        except requests.HTTPError as http_err:
            print(f"HTTP 错误: {http_err}")
        except requests.ConnectionError as conn_err:
            print(f"连接错误: {conn_err}")
        except requests.Timeout as timeout_err:
            print(f"请求超时: {timeout_err}")
        except requests.RequestException as req_err:
            print(f"请求失败: {req_err}")
        except Exception as e:
            print(f"解析播放列表时出错: {e}")

    def play_selected_item(self):
        selected_item = self.playlist.currentItem()
        if selected_item:
            url = selected_item.text().split(' - ')[1]
            media = self.vlc_instance.media_new(url)
            self.media_player.set_media(media)
            self.media_player.set_hwnd(self.graphics_view.winId())  # 设置 VLC 播放器的窗口句柄
            self.media_player.play()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.playlist:
            key = event.key()
            current_row = self.playlist.currentRow()
            if key == Qt.Key_Up:
                new_row = max(0, current_row - 1)
                self.playlist.setCurrentRow(new_row)
            elif key == Qt.Key_Down:
                new_row = min(self.playlist.count() - 1, current_row + 1)
                self.playlist.setCurrentRow(new_row)
            # 阻止默认行为，避免重复触发
            event.accept()
            return True
        return super().eventFilter(source, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())