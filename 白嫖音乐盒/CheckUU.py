import os
import webbrowser
import psutil
from concurrent.futures import ThreadPoolExecutor

class UUAcceleratorFinder:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.common_paths = [
            r'C:\Program Files\Netease\UU',
            r'C:\Program Files (x86)\Netease\UU',
            r'C:\Users\{username}\AppData\Local\Netease\UU',
            r'C:\Users\{username}\AppData\Roaming\Netease\UU'
        ]
        self.username = os.getlogin()
        self.common_paths = [path.format(username=self.username) for path in self.common_paths]

    def search_partition(self, partition_path):
        """ 在指定分区中搜索 Netease\\UU 目录下的 uu_launcher.exe，限制搜索深度 """
        def walklevel(some_dir, level=1):
            some_dir = some_dir.rstrip(os.path.sep)
            assert os.path.isdir(some_dir)
            num_sep = some_dir.count(os.path.sep)
            for root, dirs, files in os.walk(some_dir):
                yield root, dirs, files
                num_sep_this = root.count(os.path.sep)
                if num_sep + level <= num_sep_this:
                    del dirs[:]

        for root, dirs, files in walklevel(partition_path, self.max_depth):
            if 'uu_launcher.exe' in files and 'Netease' in root and 'UU' in root:
                return os.path.join(root, 'uu_launcher.exe')
        return None

    def scan_common_paths(self):
        """ 搜索常见的安装路径 """
        for path in self.common_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    if 'uu_launcher.exe' in files and 'Netease' in root and 'UU' in root:
                        return os.path.join(root, 'uu_launcher.exe')
        return None

    def scan_for_uu_accelerator(self):
        # 优先搜索常见路径
        uu_accelerator_path = self.scan_common_paths()
        if uu_accelerator_path:
            return uu_accelerator_path

        # 获取所有可用的磁盘分区
        partitions = psutil.disk_partitions()

        # 使用线程池并行搜索每个分区
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.search_partition, partition.mountpoint) for partition in partitions]
            for future in futures:
                uu_accelerator_path = future.result()
                if uu_accelerator_path:
                    return uu_accelerator_path

        return None

    def open_uu_accelerator(self):
        uu_accelerator_path = self.scan_for_uu_accelerator()
        if uu_accelerator_path:
            print(f"找到 UU 加速器: {uu_accelerator_path}")
            # 打开 UU 加速器
            os.startfile(uu_accelerator_path)
        else:
            print("未找到 UU 加速器，正在打开官网...")
            self.open_uu_accelerator_website()

    def open_uu_accelerator_website(self):
        webbrowser.open('https://uu.163.com/')

# 示例用法
if __name__ == '__main__':
    finder = UUAcceleratorFinder()
    finder.open_uu_accelerator()