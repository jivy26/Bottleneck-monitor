import json
import os

DEFAULT_CONFIG = {
    "refresh_rate": 500,
    "history_size": 60,
    "dark_mode": True,
    "thresholds": {
        "cpu_warning": 90,
        "gpu_warning": 90,
        "ram_warning": 90,
        "temp_warning": 80
    },
    "graph_colors": {
        "cpu": "#00ff00",
        "gpu": "#0000ff",
        "ram": "#ff0000",
        "temp": "#ff00ff"
    }
}

class Config:
    def __init__(self):
        self.config_file = "settings.json"
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.settings = {**DEFAULT_CONFIG, **json.load(f)}
            else:
                self.settings = DEFAULT_CONFIG
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.settings = DEFAULT_CONFIG
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}") 