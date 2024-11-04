import sys
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QSplitter, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from faker import Faker

# 免税州列表
tax_free_states = ['AK', 'DE', 'MT', 'NH', 'OR']

def generate_tax_free_us_address_and_phone():
    fake = Faker('en_US')
    
    # 生成随机地址
    street_address = fake.street_address()
    state = fake.random_element(tax_free_states)
    city = fake.city()
    zipcode = fake.zipcode_in_state(state_abbr=state)
    
    # 生成随机电话号码
    phone_number = fake.phone_number()
    
    # 组合成完整的地址
    full_address = f"{street_address}\n{city}, {state} {zipcode}"
    
    return full_address, phone_number

def extract_address_components(address):
    components = address.split('\n')
    if len(components) < 2:
        return None, None, None
    
    street = components[0]
    city_state_zip = components[1]
    
    city_state_zip_parts = city_state_zip.split(',')
    if len(city_state_zip_parts) < 2:
        return None, None, None
    
    city = city_state_zip_parts[0].strip()
    state_zip = city_state_zip_parts[1].strip()
    
    state_zip_parts = state_zip.split()
    if len(state_zip_parts) < 2:
        return None, None, None
    
    state = state_zip_parts[0]
    zipcode = state_zip_parts[1]
    
    return city, state, zipcode

class AddressGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('美国免税州地址生成器')
        self.setFixedSize(800, 400)  # 固定窗口大小
        
        main_layout = QHBoxLayout()
        
        # 左侧布局
        left_layout = QVBoxLayout()
        
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # 设置文本框为只读
        left_layout.addWidget(self.text_edit)
        
        self.generate_button = QPushButton('生成地址和电话', self)
        self.generate_button.clicked.connect(self.generate_and_display)
        left_layout.addWidget(self.generate_button)
        
        self.register_button = QPushButton('注册贝宝美国账号', self)
        self.register_button.clicked.connect(self.open_paypal_registration)
        left_layout.addWidget(self.register_button)
        
        left_frame = QFrame(self)
        left_frame.setLayout(left_layout)
        
        # 右侧布局
        right_layout = QVBoxLayout()
        
        self.tutorial_text = QTextEdit(self)
        self.tutorial_text.setReadOnly(True)  # 设置文本框为只读
        self.tutorial_text.setPlainText(
            "教程:\n"
            "1. 点击“注册贝宝美国账号”按钮，打开 PayPal 注册页面。"
            "注册账号时，可以使用中国手机号码注册，国家选择美国就可以，"
            "有些银行卡可能不支持境外支付，建行有些需要自己开通境外支付。"
            "2.翻墙或者用UU加速器，什么加速器都可以，加速美国\n"
            "3.打开Steam随便选个游戏，点击加入购物车，加入之后查看购物车,点击国家，选择“美国”,是我的账单地址位于美国\n"
            "4.切换完之后移除掉购物车游戏就好\n"
            "5.点击steam商店主页，搜索“index”,选择控制器 269那款\n"
            "6.使用免税州生成器生成地址，填邮寄地址\n"
            "7,买完直接退款，结束\n"
        )
        right_layout.addWidget(self.tutorial_text)
        
        right_frame = QFrame(self)
        right_frame.setLayout(right_layout)
        
        # 使用 QSplitter 将左右布局分开
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def generate_and_display(self):
        address, phone_number = generate_tax_free_us_address_and_phone()
        city, state, zipcode = extract_address_components(address)
        
        if city and state and zipcode:
            display_text = (
                f"生成的美国快递邮寄地址 (地址):  {address}\n"
                f"生成的电话号码 (电话):          {phone_number}\n"
                f"邮编 (邮编):                    {zipcode}\n"
                f"城市 (城市):                    {city}\n"
                f"州 (州):                        {state}"
            )
        else:
            display_text = (
                "生成的地址格式不正确，无法提取城市、州和邮编。\n"
                f"生成的美国快递邮寄地址 (地址): {address}\n"
                f"生成的电话号码 (电话): {phone_number}"
            )
        
        self.text_edit.setPlainText(display_text)

    def open_paypal_registration(self):
        webbrowser.open('https://www.paypal.com/c2/webapps/mpp/account-selection')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AddressGeneratorApp()
    ex.show()
    sys.exit(app.exec_())