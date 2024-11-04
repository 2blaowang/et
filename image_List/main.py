import os
import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QTabWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Steam URLs to get top and new games
STEAM_TOP_URL = "https://store.steampowered.com/search/?filter=topsellers"
STEAM_NEW_URL = "https://store.steampowered.com/search/?filter=recently_released"
RESOURCE_DIR = "resources"

class GameImageWidget(QWidget):
    def __init__(self, game_name, image_path):
        super().__init__()
        layout = QHBoxLayout()
        self.image_label = QLabel()
        self.load_image(image_path)
        self.label = QLabel(game_name)
        layout.addWidget(self.image_label)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def load_image(self, path):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        else:
            print(f"Image not found at {path}")

class GameLoaderThread(QThread):
    game_loaded = pyqtSignal(str, str)  # Signal to emit when a game is loaded

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                game_elements = soup.find_all('a', class_='search_result_row')
                print(f"Number of games fetched: {len(game_elements)}")
                for game in game_elements[:10]:  # Display top 10 games
                    game_name = game.find('span', class_='title').text.strip()
                    image_url = game.find('img')['src']
                    print(f"Game: {game_name}, Image URL: {image_url}")
                    image_path = os.path.join(RESOURCE_DIR, f"{game_name}.jpg")
                    self.download_image(image_url, image_path)
                    self.game_loaded.emit(game_name, image_path)
            else:
                print(f"Failed to fetch data from Steam website. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching data from Steam website: {e}")

    def download_image(self, url, path):
        try:
            data = requests.get(url).content
            with open(path, 'wb') as file:
                file.write(data)
            print(f"Downloaded image to {path}")
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")

class GameTab(QWidget):
    def __init__(self, title, url):
        super().__init__()
        self.title = title
        self.url = url
        self.games = []
        self.game_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        # Add the scroll area to the main layout
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def load_games(self):
        self.game_loader_thread = GameLoaderThread(self.url)
        self.game_loader_thread.game_loaded.connect(self.add_game)
        self.game_loader_thread.start()

    def add_game(self, game_name, image_path):
        self.games.append((game_name, image_path))
        self.display_game(game_name, image_path)

    def display_game(self, game_name, image_path):
        game_widget = GameImageWidget(game_name, image_path)
        self.game_widgets.append(game_widget)
        self.scroll_layout.addWidget(game_widget)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steam 游戏")
        self.setGeometry(100, 100, 800, 600)

        # Check and create resource directory
        if not os.path.exists(RESOURCE_DIR):
            os.makedirs(RESOURCE_DIR)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.top_games_tab = GameTab("热门游戏", STEAM_TOP_URL)
        self.new_games_tab = GameTab("最新游戏", STEAM_NEW_URL)
        self.tab_widget.addTab(self.top_games_tab, "热门游戏")
        self.tab_widget.addTab(self.new_games_tab, "最新游戏")

        # Connect tab change event to load games
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Set the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # Load top games by default
        self.top_games_tab.load_games()

    def on_tab_changed(self, index):
        current_tab = self.tab_widget.widget(index)
        if not current_tab.games:
            current_tab.load_games()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())