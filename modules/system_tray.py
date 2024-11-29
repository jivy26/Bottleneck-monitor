from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
import os

class SystemTray(QSystemTrayIcon):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_tray()
        
    def setup_tray(self):
        menu = QMenu()
        
        show_action = menu.addAction("Show/Hide")
        show_action.triggered.connect(self.toggle_window)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.main_window.close)
        
        self.setContextMenu(menu)
        
        icon_path = os.path.join("resources", "icon.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            
        self.show()
        
    def toggle_window(self):
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.activateWindow() 