import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt  # 导入 Qt 模块
from aip import AipImageSearch
from PIL import Image
import os
import requests
from io import BytesIO

# 你的 APPID AK SK
APP_ID = '116114576'
API_KEY = '3NGTJx8mjHd5475soEwYYWpp'
SECRET_KEY = 'bfUJfxhp3iL3DGImfIqgwXWGiWAMksq7'

# 初始化 AipImageSearch 对象
client = AipImageSearch(APP_ID, API_KEY, SECRET_KEY)

# 读取图片
def get_file_content(filePath):
    try:
        with open(filePath, 'rb') as fp:
            return fp.read()
    except FileNotFoundError:
        print(f"文件未找到: {filePath}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None

# 下载网络图片
def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.RequestException as e:
        print(f"下载图片时发生错误: {e}")
        return None

# 图片入库
def add_image_to_library(image, brief=""):
    if image is not None:
        response = client.sameHqAdd(image, brief)
        if 'error_code' in response:
            print(f"入库失败: {response}")
            return False
        else:
            print("入库成功")
            return True
    else:
        print("无法读取图片，入库失败")
        return False

# 搜索图片
def search_image(image):
    if image is not None:
        result = client.sameHqSearch(image)
        if 'error_code' in result:
            print(f"搜索失败: {result}")
            return None
        else:
            print("搜索结果:")
            if 'result' in result and result['result']:
                for item in result['result']:
                    print(f"Score: {item['score']}, Brief: {item['brief']}")
                return result['result']
            else:
                print("No similar images found.")
                return []
    else:
        print("无法读取图片，搜索失败")
        return None

class ImageSelectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图片选择和处理')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel('请选择图片或输入图片URL', self)
        layout.addWidget(self.label)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.local_button = QPushButton('选择本地图片', self)
        self.local_button.clicked.connect(self.select_local_image)
        layout.addWidget(self.local_button)

        self.url_label = QLabel('图片URL:', self)
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit(self)
        layout.addWidget(self.url_input)

        self.url_button = QPushButton('加载网络图片', self)
        self.url_button.clicked.connect(self.load_url_image)
        layout.addWidget(self.url_button)

        self.add_button = QPushButton('添加到图库', self)
        self.add_button.clicked.connect(self.add_image)
        layout.addWidget(self.add_button)

        self.search_button = QPushButton('搜索图片', self)
        self.search_button.clicked.connect(self.search_image)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def select_local_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options)
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(300, 300))
            self.image_label.setAlignment(Qt.AlignCenter)

    def load_url_image(self):
        url = self.url_input.text().strip()
        if url:
            image_data = download_image(url)
            if image_data:
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.getvalue())
                self.image_label.setPixmap(pixmap.scaled(300, 300))
                self.image_label.setAlignment(Qt.AlignCenter)
                self.image_path = url
            else:
                QMessageBox.warning(self, '警告', '无法下载图片，请检查URL')

    def add_image(self):
        if hasattr(self, 'image_path'):
            if isinstance(self.image_path, str) and self.image_path.startswith('http'):
                image_data = download_image(self.image_path)
                if image_data:
                    add_image_to_library(image_data.getvalue())
                else:
                    QMessageBox.warning(self, '警告', '无法下载图片，请检查URL')
            else:
                image_data = get_file_content(self.image_path)
                if image_data:
                    add_image_to_library(image_data)
                else:
                    QMessageBox.warning(self, '警告', '无法读取图片，请检查路径')
        else:
            QMessageBox.warning(self, '警告', '请先选择或加载图片')

    def search_image(self):
        if hasattr(self, 'image_path'):
            if isinstance(self.image_path, str) and self.image_path.startswith('http'):
                image_data = download_image(self.image_path)
                if image_data:
                    results = search_image(image_data.getvalue())
                    if results:
                        QMessageBox.information(self, '搜索结果', f"找到相似图片: {len(results)}张")
                    else:
                        QMessageBox.information(self, '搜索结果', '未找到相似图片')
                else:
                    QMessageBox.warning(self, '警告', '无法下载图片，请检查URL')
            else:
                image_data = get_file_content(self.image_path)
                if image_data:
                    results = search_image(image_data)
                    if results:
                        QMessageBox.information(self, '搜索结果', f"找到相似图片: {len(results)}张")
                    else:
                        QMessageBox.information(self, '搜索结果', '未找到相似图片')
                else:
                    QMessageBox.warning(self, '警告', '无法读取图片，请检查路径')
        else:
            QMessageBox.warning(self, '警告', '请先选择或加载图片')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageSelectionApp()
    ex.show()
    sys.exit(app.exec_())