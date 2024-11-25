import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

def download_image(url):
    """从网络下载图片并返回Image对象"""
    response = requests.get(url)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    print(f"Downloaded image from {url} with size {image.size}")
    return image

def update_carousel(index=0):
    """更新轮播框中的图片"""
    if index >= len(images):
        index = 0
    image = images[index]
    
    # 设置固定的宽度和高度
    label_width = 3858
    label_height = 2160
    
    # 计算图片的缩放比例
    img_width, img_height = image.size
    ratio = min(label_width / img_width, label_height / img_height)
    
    # 缩放图像以适应轮播框
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # 将图片放置在标签的中心
    bg_image = Image.new('RGB', (label_width, label_height), (255, 255, 255))  # 创建一个白色背景
    bg_image.paste(image, ((label_width - new_width) // 2, (label_height - new_height) // 2))
    
    photo = ImageTk.PhotoImage(bg_image)
    carousel_label.config(image=photo)
    carousel_label.image = photo  # 保持引用，防止垃圾回收
    root.after(3000, lambda: update_carousel(index + 1))  # 每3秒切换一次图片

# 创建主窗口
root = tk.Tk()
root.title("渐变色背景")
root.geometry("800x600")  # 设置窗口大小

# 定义起始和结束颜色
start_color = [144, 238, 144]  # 柔和的绿色
end_color = [255, 182, 193]    # 柔和的红色

# 生成渐变颜色序列
def generate_gradient_colors(start_color, end_color, num_steps=1000):
    """生成渐变颜色序列"""
    step_size = [(end_color[i] - start_color[i]) / num_steps for i in range(3)]
    colors = []
    for i in range(num_steps):
        color = [int(start_color[j] + i * step_size[j]) for j in range(3)]
        colors.append(color)
    return colors

def update_background(index=0):
    """更新背景颜色"""
    if index >= len(colors):
        index = 0
    root.config(bg=rgb_to_hex(colors[index]))
    root.after(100, lambda: update_background(index + 1))  # 每100毫秒更新一次

def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB元组"""
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def rgb_to_hex(rgb):
    """将RGB元组转换为十六进制颜色"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

# 生成渐变颜色序列
colors = generate_gradient_colors(start_color, end_color, num_steps=1000)

# 开始更新背景颜色
update_background()

# 下载网络图片
image_urls = [
    "https://www.toopic.cn/public/uploads/small/1704264337798170426433788.jpg",
    "https://www.toopic.cn/public/uploads/small/1704215542946170421554257.jpg",
    "https://www.toopic.cn/public/uploads/small/1715140728331171514072863.jpg",
    "https://www.toopic.cn/public/uploads/small/1704264340828170426434044.jpg"
]

images = [download_image(url) for url in image_urls]

# 创建轮播框
carousel_label = tk.Label(root, height=200)
carousel_label.pack(pady=100, padx=100)  # 使用pady和padx使轮播框居中并设置左右间距

# 延迟启动轮播，确保标签尺寸正确
root.update_idletasks()  # 强制更新窗口
root.after(2000, update_carousel)  # 延迟2秒后启动轮播

# 运行主循环
root.mainloop()