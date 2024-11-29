import win32gui
import win32api
import time
from typing import Dict, Optional

class InputMonitor:
    def __init__(self):
        self.last_input_time = time.time()
        self.input_delays = []
        
    def measure_input_lag(self, hwnd: int) -> Optional[float]:
        try:
            current_time = time.time()
            msg_time = win32gui.GetMessageTime()
            
            if msg_time:
                delay_ms = (current_time - (msg_time / 1000.0)) * 1000
                self.input_delays.append(delay_ms)
                
                if len(self.input_delays) > 100:
                    self.input_delays.pop(0)
                    
                return sum(self.input_delays) / len(self.input_delays)
        except:
            return None 