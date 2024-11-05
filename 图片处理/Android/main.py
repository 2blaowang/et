from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from image_processor import apply_blur_and_gradient
import os

class ImageBlurApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 选择输入图片
        self.input_label = Label(text='选择输入图片:')
        self.layout.add_widget(self.input_label)

        self.input_button = Button(text='选择图片', on_release=self.select_input_image)
        self.layout.add_widget(self.input_button)

        # 设置模糊半径
        self.radius_label = Label(text='模糊半径:')
        self.layout.add_widget(self.radius_label)

        self.radius_slider = Slider(min=1, max=50, value=10, step=1)
        self.radius_slider.bind(value=self.update_radius_label)
        self.layout.add_widget(self.radius_slider)

        self.radius_value_label = Label(text=f'当前模糊半径: {self.radius_slider.value}')
        self.layout.add_widget(self.radius_value_label)

        # 选择输出文件夹
        self.output_label = Label(text='选择输出文件夹:')
        self.layout.add_widget(self.output_label)

        self.output_path_edit = TextInput(hint_text='输出文件夹路径')
        self.layout.add_widget(self.output_path_edit)

        self.output_button = Button(text='选择文件夹', on_release=self.select_output_folder)
        self.layout.add_widget(self.output_button)

        # 处理按钮
        self.process_button = Button(text='处理图片', on_release=self.process_image)
        self.layout.add_widget(self.process_button)

        return self.layout

    def select_input_image(self, instance):
        content = FileChooserListView(path='.')
        popup = Popup(title='选择图片', content=content, size_hint=(0.9, 0.9))
        content.bind(selection=lambda x: self.set_input_image(popup, x[0] if x else None))
        popup.open()

    def set_input_image(self, popup, path):
        if path:
            self.input_image_path = path
        popup.dismiss()

    def select_output_folder(self, instance):
        content = FileChooserListView(path='.', filters=['dir'])
        popup = Popup(title='选择文件夹', content=content, size_hint=(0.9, 0.9))
        content.bind(selection=lambda x: self.set_output_folder(popup, x[0] if x else None))
        popup.open()

    def set_output_folder(self, popup, path):
        if path:
            self.output_path_edit.text = path
        popup.dismiss()

    def update_radius_label(self, instance, value):
        self.radius_value_label.text = f'当前模糊半径: {int(value)}'

    def process_image(self, instance):
        try:
            input_image_path = self.input_image_path
            output_folder = self.output_path_edit.text
            blur_radius = int(self.radius_slider.value)

            if not input_image_path or not output_folder:
                raise ValueError("请输入图片路径和输出文件夹")

            success, message = apply_blur_and_gradient(input_image_path, output_folder, blur_radius)
            self.show_message(message)
        except Exception as e:
            self.show_message(f"处理失败: {str(e)}")

    def show_message(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        ok_button = Button(text='确定')
        content.add_widget(ok_button)
        popup = Popup(title='消息', content=content, size_hint=(0.5, 0.3))
        ok_button.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    ImageBlurApp().run()