import json
import os
from typing import Dict, List

class GameOptimizer:
    def __init__(self):
        self.optimization_db = {
            "FortniteClient-Win64-Shipping.exe": {
                "nvidia_settings": {
                    "prefer_maximum_performance": True,
                    "threaded_optimization": "On",
                    "low_latency_mode": "Ultra"
                },
                "windows_settings": {
                    "game_mode": True,
                    "hardware_accelerated_gpu_scheduling": True
                },
                "suggestions": [
                    "Set 'Allow for Multithreaded Rendering' in game settings",
                    "Disable 'Show FPS' for better performance",
                    "Use Performance Mode for competitive play"
                ]
            }
        }
        
    def get_optimization_tips(self, process_name: str, metrics: Dict) -> List[str]:
        tips = []
        game_settings = self.optimization_db.get(process_name, {})
        
        if metrics['cpu_percent'] > 80:
            tips.append("High CPU usage detected:")
            tips.extend([
                "- Close background applications",
                "- Update CPU drivers",
                "- Check CPU thermal paste"
            ])
            
        if metrics.get('gpu', {}).get('utilization', 0) < 70:
            tips.append("Low GPU utilization detected:")
            tips.extend([
                "- Enable GPU scheduling in Windows",
                "- Update GPU drivers",
                "- Check power management settings"
            ])
            
        if game_settings:
            tips.extend(game_settings.get('suggestions', []))
            
        return tips 