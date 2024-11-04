import sys
import requests
import time
import urllib3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("阿奎搜索器")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.search_edit = QLineEdit(self)
        self.layout.addWidget(self.search_edit)

        self.search_button = QPushButton("Search", self)
        self.layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.search_images)

        self.image_list = QListWidget(self)
        self.layout.addWidget(self.image_list)

    def search_images(self):
        query = self.search_edit.text()
        if not query:
            return

        api_key = "AIzaSyBKBr_RVY24y8oD9hE8PYtClUO0hR_Jx1E"
        cx = "13d6806c1cfbc409b"
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&num=10&searchType=image&key={api_key}&cx={cx}"

        response = requests.get(url, timeout=30, verify=True)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            self.display_images(items)
        else:
            print(f"请求失败，状态码: {response.status_code}")

    def display_images(self, items):
        self.image_list.clear()
        for item in items:
            image_url = item["link"]
            label = QLabel(self)
            pixmap = self.load_image_from_url(image_url)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            list_item = QListWidgetItem(self.image_list)
            list_item.setSizeHint(label.sizeHint())
            self.image_list.addItem(list_item)
            self.image_list.setItemWidget(list_item, label)

    def load_image_from_url(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30, verify=True)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    return pixmap
                else:
                    print(f"请求失败，状态码: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 等待 1 秒后重试
        return QPixmap()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())