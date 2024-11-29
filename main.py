import sys
import json
import os
from PyQt6.QtWidgets import QApplication
from modules.gui import MainWindow

CONFIG_FILE = "last_session.json"

def save_last_process(pid):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'last_pid': pid}, f)
    except Exception as e:
        print(f"Warning: Could not save last process: {e}")

def load_last_process():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_pid')
    except Exception as e:
        print(f"Warning: Could not load last process: {e}")
    return None

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    last_pid = load_last_process()
    if last_pid:
        for i in range(window.process_selector.count()):
            if window.process_selector.itemData(i) == last_pid:
                window.process_selector.setCurrentIndex(i)
                break
    
    window.process_selector.currentIndexChanged.connect(
        lambda: save_last_process(window.process_selector.currentData())
    )
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 