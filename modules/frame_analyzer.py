import numpy as np
from typing import List, Dict

class FrameAnalyzer:
    def __init__(self):
        self.frame_times = []
        self.stutter_threshold = 1.5
        
    def analyze_frame_times(self, new_frame_time: float) -> Dict:
        self.frame_times.append(new_frame_time)
        if len(self.frame_times) > 300:
            self.frame_times.pop(0)
            
        frame_times = np.array(self.frame_times)
        
        return {
            'avg_frame_time': np.mean(frame_times),
            '1%_low': np.percentile(frame_times, 1),
            '0.1%_low': np.percentile(frame_times, 0.1),
            'frame_time_variance': np.var(frame_times),
            'stutters_detected': np.sum(frame_times > (np.mean(frame_times) * self.stutter_threshold)),
            'frame_pacing': self._analyze_frame_pacing(frame_times)
        }
        
    def _analyze_frame_pacing(self, frame_times: np.ndarray) -> str:
        variance = np.var(frame_times)
        if variance < 0.1:
            return "Excellent"
        elif variance < 0.3:
            return "Good"
        elif variance < 0.5:
            return "Fair"
        else:
            return "Poor" 