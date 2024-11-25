pip install -r requirements.txt

pyinstaller --onefile --windowed --add-binary "C:\Program Files\VideoLAN\VLC:." --icon=icon.png main.py

python main.py