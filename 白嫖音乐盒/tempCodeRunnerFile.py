import sys
import webbrowser
import json
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QProgressBar, QMessageBox, QDialogButtonBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt  # 添加 Qt 导入
from PyQt5.QtGui import QPixmap, QPalette, QBrush  # 导入 QBrush
from The_US_Addr import generate_tax_free_addresses
from baipiao import SteamScraper

class SteamScrapeThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        try:
            scraper = SteamScraper()
            scraper.scrape_steam_data(self.username, self.password)
            self.finished.emit("操作成功")
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

class TutorialWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show_startup_dialog()  # 显示启动对话框
        self.center_window()  # 将窗口居中显示

    def initUI(self):
        # 设置主布局
        main_layout = QHBoxLayout()

        # 左侧文本框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)  # 设置为只读
        self.text_edit.setText("""
1. 点击“注册贝宝美国账号”按钮，打开 PayPal 注册页面。注册账号时，可以使用中国手机号码注册，国家选择美国就可以。有些银行卡可能不支持境外支付，建行有些需要自己开通境外支付。
2. 翻墙或者用UU加速器，什么加速器都可以，加速美国。
3. 在输入框输入账号密码，打开Steam就可以自动登录，只需要Steam验证就好。
4. 切换国家(自动)。
5. 点击Steam商店主页，搜索“index”，选择控制器 269 那款(自动)。
6. 使用免税州生成器生成地址，填邮寄地址(手动)。
7. 买完直接退款，结束(没有做😄)。
""")

        # 右侧布局
        right_layout = QVBoxLayout()

        # 顶部输入框布局
        input_layout = QVBoxLayout()

        # Steam账号输入框
        self.steam_username_input = QLineEdit()
        self.steam_username_input.setPlaceholderText("请输入Steam账号")
        input_layout.addWidget(self.steam_username_input)

        # Steam密码输入框
        self.steam_password_input = QLineEdit()
        self.steam_password_input.setPlaceholderText("请输入Steam密码")
        self.steam_password_input.setEchoMode(QLineEdit.Password)  # 设置为密码模式
        input_layout.addWidget(self.steam_password_input)

        # 按钮布局
        button_layout = QVBoxLayout()
        
        # 创建按钮
        btn_paypal = QPushButton('注册贝宝美国账号')
        btn_steam = QPushButton('打开Steam')
        btn_refund = QPushButton('退款')
        btn_tax_free_address = QPushButton('美国免税州地址生成器')
        btn_get_badge = QPushButton('获取勋章')  # 新增按钮
        
        # 绑定按钮点击事件
        btn_paypal.clicked.connect(self.open_paypal_registration)
        btn_steam.clicked.connect(self.open_steam)
        btn_refund.clicked.connect(self.refund)
        btn_tax_free_address.clicked.connect(self.generate_tax_free_address)  # 实现功能
        btn_get_badge.clicked.connect(self.get_badge)  # 新增按钮的点击事件

        # 将按钮添加到按钮布局
        button_layout.addWidget(btn_paypal)
        button_layout.addWidget(btn_steam)
        button_layout.addWidget(btn_refund)
        button_layout.addWidget(btn_tax_free_address)
        button_layout.addWidget(btn_get_badge)  # 新增按钮添加到布局
        button_layout.addStretch(1)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFC0CB, stop:0.5 #FF69B4, stop:1.0 #FF1493);
                border-radius: 5px;
            }
        """)
        button_layout.addWidget(self.progress_bar)

        # 将输入框布局和按钮布局添加到右侧布局
        right_layout.addLayout(input_layout)
        right_layout.addLayout(button_layout)

        # 将文本框和右侧布局添加到主布局
        main_layout.addWidget(self.text_edit)
        main_layout.addLayout(right_layout)

        # 设置窗口的主布局
        self.setLayout(main_layout)

        # 设置窗口背景图片
        palette = self.palette()
        background_image = QPixmap("Loading.jpg")
        brush = QBrush(background_image)
        palette.setBrush(QPalette.Window, brush)
        self.setPalette(palette)

        # 设置窗口标题和大小
        self.setWindowTitle('教程窗口')
        self.setGeometry(300, 300, 600, 400)

    def center_window(self):
        # 获取屏幕的几何尺寸
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width, screen_height = screen_geometry.width(), screen_geometry.height()

        # 获取窗口的几何尺寸
        window_size = self.frameGeometry()
        window_width, window_height = window_size.width(), window_size.height()

        # 计算窗口的位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 设置窗口的位置
        self.move(x, y)

    def show_startup_dialog(self):
        # 创建消息框
        msg_box = QMessageBox()
        msg_box.setWindowTitle("启动提示")
        msg_box.setText("""温馨提示：这不是病毒软件，请放心使用！\n
全程采用模拟登录，不保留数据，完全可以放心，退出之后所有\n
数据都会清除\n
这个软件并不完整，后续还会继续完善，目前完成了大部分需求\n
可以直接选择UU加速器免费加速steam美服商店，一定要加速！\n
“或者翻墙也行”\n
❗❗❗ 警告：转区可能会异地红（看脸🤭）❗❗❗\n
可以先保存一份自己在steam的购买记录,steam凭证微信支付宝邮箱截图等，方便申诉\n
点击yes打开 UU加速器(可能会慢一点)，No直接进入应用\n
""")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # 显示消息框并获取用户选择
        result = msg_box.exec_()

        if result == QMessageBox.Yes:
            self.open_uu_accelerator()
        else:
            self.text_edit.append("未选择打开UU加速器，直接进入应用。")

    def open_uu_accelerator(self):
        finder = UUAcceleratorFinder()
        finder.open_uu_accelerator()

    def open_paypal_registration(self):
        webbrowser.open('https://www.paypal.com/us/welcome/signup/#/login_info')

    def open_steam(self):
        # 从输入框获取账号和密码
        username = self.steam_username_input.text()
        password = self.steam_password_input.text()

        # 显示进度条
        self.progress_bar.setVisible(True)

        # 启动线程
        self.steam_thread = SteamScrapeThread(username, password)
        self.steam_thread.finished.connect(self.on_scrape_finished)
        self.steam_thread.start()

    def on_scrape_finished(self, result):
        # 隐藏进度条
        self.progress_bar.setVisible(False)

        # 处理结果
        if "Error" in result:
            self.text_edit.append(f"错误: {result}")
        else:
            self.text_edit.append(f"成功: {result}")

    def refund(self):
        # 这里可以添加退款相关的逻辑
        print("退款功能暂未实现")

    def generate_tax_free_address(self):
        # 调用 generate_tax_free_addresses 方法生成地址信息
        addresses = generate_tax_free_addresses()
        
        # 随机选择一个地址
        address_info = random.choice(addresses)
        
        # 构建地址信息字符串
        address_text = f"地址: {address_info['地址']}\n" \
                       f"城市: {address_info['城市']}\n" \
                       f"州: {address_info['州']}\n" \
                       f"邮编: {address_info['邮编']}\n" \
                       f"电话: {address_info['电话']}"

        # 使用QMessageBox显示地址信息
        msg_box = QMessageBox()
        msg_box.setWindowTitle("美国免税州地址")
        msg_box.setText(address_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 使文本可选
        msg_box.exec_()

    def get_badge(self):
        # 这里可以添加获取勋章的逻辑
        print("获取勋章功能暂未实现")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TutorialWindow()
    window.resize(800, 800)
    window.show()
    window.center_window()
    sys.exit(app.exec_())