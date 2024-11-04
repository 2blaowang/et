import tkinter as tk
from tkinter import ttk
import json

# 读取存储的游戏数据
with open('games.json', 'r') as f:
    games = json.load(f)

# 创建主窗口
root = tk.Tk()
root.title("Steam Games List")

# 创建搜索框
search_var = tk.StringVar()
search_box = ttk.Entry(root, textvariable=search_var, width=50)
search_box.pack(fill=tk.X, padx=5, pady=5)
search_box.insert(0, "Search by ID or Name")  # 设置提示语

# 定义搜索函数
def search_games(event=None):
    query = search_var.get().strip().lower()
    if query == "search by id or name":
        query = ""
    
    # 清空当前显示的项目
    for item in tree.get_children():
        tree.delete(item)
    
    # 过滤并显示匹配的游戏
    if query:
        filtered_games = [game for game in games if query in str(game['appid']).lower() or query in game['name'].lower()]
    else:
        filtered_games = games
    
    for game in filtered_games:
        app_id = game['appid']
        name = game['name']
        tree.insert("", "end", values=(app_id, name))

# 延迟搜索
def debounce_search(event):
    global search_after_id
    if search_after_id is not None:
        root.after_cancel(search_after_id)
    search_after_id = root.after(300, search_games)

# 全局变量用于存储延迟搜索的 ID
search_after_id = None

# 绑定搜索框的回车键事件和键盘释放事件
search_box.bind("<Return>", search_games)
search_box.bind("<KeyRelease>", debounce_search)
search_box.bind("<FocusIn>", lambda event: search_box.delete(0, tk.END) if search_var.get() == "Search by ID or Name" else None)
search_box.bind("<FocusOut>", lambda event: search_box.insert(0, "Search by ID or Name") if search_var.get().strip() == "" else None)

# 创建 Treeview 控件
tree = ttk.Treeview(root, columns=("ID", "Name"), show="headings")
tree.heading("ID", text="App ID")
tree.heading("Name", text="Name")
tree.column("ID", width=100)
tree.column("Name", width=300)

# 添加滚动条
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scrollbar.set)

# 插入初始游戏数据
for game in games:
    app_id = game['appid']
    name = game['name']
    tree.insert("", "end", values=(app_id, name))

# 绑定单击事件
def on_single_click(event):
    item = tree.identify_row(event.y)
    if item:
        app_id = tree.item(item, "values")[0]
        root.clipboard_clear()
        root.clipboard_append(app_id)
        root.update()  # 确保剪贴板内容立即更新

tree.bind("<Button-1>", on_single_click)

# 包装 Treeview
tree.pack(fill=tk.BOTH, expand=True)

# 运行主循环
root.mainloop()