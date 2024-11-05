import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QSlider, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from image_processor import apply_blur_and_gradient

class ImageBlurApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图片模糊化并添加渐变效果')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # 选择输入图片
        self.input_label = QLabel('选择输入图片:', self)
        layout.addWidget(self.input_label)

        self.input_button = QPushButton('选择图片', self)
        self.input_button.clicked.connect(self.select_input_image)
        layout.addWidget(self.input_button)

        # 设置模糊半径
        self.radius_label = QLabel('模糊半径:', self)
        layout.addWidget(self.radius_label)

        self.radius_slider = QSlider(Qt.Horizontal, self)
        self.radius_slider.setMinimum(1)
        self.radius_slider.setMaximum(50)
        self.radius_slider.setValue(10)
        self.radius_slider.valueChanged.connect(self.update_radius_label)
        layout.addWidget(self.radius_slider)

        self.radius_value_label = QLabel(f'当前模糊半径: {self.radius_slider.value()}', self)
        layout.addWidget(self.radius_value_label)

        # 选择输出文件夹
        self.output_label = QLabel('选择输出文件夹:', self)
        layout.addWidget(self.output_label)

        self.output_path_edit = QLineEdit(self)
        layout.addWidget(self.output_path_edit)

        self.output_button = QPushButton('选择文件夹', self)
        self.output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.output_button)

        # 处理按钮
        self.process_button = QPushButton('处理图片', self)
        self.process_button.clicked.connect(self.process_image)
        layout.addWidget(self.process_button)

        self.setLayout(layout)

    def select_input_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        if file_name:
            self.input_image_path = file_name

    def select_output_folder(self):
        options = QFileDialog.Options()
        folder_name = QFileDialog.getExistingDirectory(self, "选择文件夹", options=options)
        if folder_name:
            self.output_path_edit.setText(folder_name)

    def update_radius_label(self, value):
        self.radius_value_label.setText(f'当前模糊半径: {value}')

    def process_image(self):
        try:
            input_image_path = self.input_image_path
            output_folder = self.output_path_edit.text()
            blur_radius = self.radius_slider.value()

            if not input_image_path or not output_folder:
                raise ValueError("请输入图片路径和输出文件夹")

            success, message = apply_blur_and_gradient(input_image_path, output_folder, blur_radius)
            self.show_message(message)
        except Exception as e:
            self.show_message(f"处理失败: {str(e)}")

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("消息")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageBlurApp()
    ex.show()
    sys.exit(app.exec_())