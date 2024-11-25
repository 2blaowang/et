import tkinter as tk
import time
import random

def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB元组"""
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def rgb_to_hex(rgb):
    """将RGB元组转换为十六进制颜色"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

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

# 创建主窗口
root = tk.Tk()
root.title("渐变色背景")
root.geometry("800x600")  # 设置窗口大小

# 定义起始和结束颜色
start_color = [144, 238, 144]  # 柔和的绿色
end_color = [255, 182, 193]    # 柔和的红色

# 生成渐变颜色序列
colors = generate_gradient_colors(start_color, end_color, num_steps=1000)

# 开始更新背景颜色
update_background()

# 运行主循环
root.mainloop()