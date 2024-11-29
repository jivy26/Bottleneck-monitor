import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
import logger

@dataclass
class BottleneckResult:
    exists: bool
    component: Optional[str]
    severity: float  # 0-1 scale
    description: str

class BottleneckAnalyzer:
    def __init__(self):
        self.HIGH_USAGE_THRESHOLD = 90.0
        self.LOW_USAGE_THRESHOLD = 30.0
        
    def analyze(self, process_metrics, system_metrics):
        """Analyze metrics to detect bottlenecks"""
        try:
            cpu_usage = process_metrics['cpu_percent']
            gpu_info = system_metrics.get('gpu', {})
            gpu_usage = gpu_info.get('utilization', 0)
            memory_percent = process_metrics['memory_percent']
            
            # CPU Bottleneck
            if cpu_usage > self.HIGH_USAGE_THRESHOLD and gpu_usage < self.LOW_USAGE_THRESHOLD:
                severity = min((cpu_usage - self.HIGH_USAGE_THRESHOLD) / 10.0, 1.0)
                return BottleneckResult(True, "CPU", severity, "CPU bottleneck detected")
                
            # GPU Bottleneck
            if gpu_usage > self.HIGH_USAGE_THRESHOLD and cpu_usage < self.LOW_USAGE_THRESHOLD:
                severity = min((gpu_usage - self.HIGH_USAGE_THRESHOLD) / 10.0, 1.0)
                return BottleneckResult(True, "GPU", severity, "GPU bottleneck detected")
                
            # Memory Bottleneck
            if memory_percent > self.HIGH_USAGE_THRESHOLD:
                severity = min((memory_percent - self.HIGH_USAGE_THRESHOLD) / 10.0, 1.0)
                return BottleneckResult(True, "RAM", severity, "Memory bottleneck detected")
                
            return BottleneckResult(False, None, 0.0, "No bottleneck detected")
            
        except Exception as e:
            logger.error(f"Error in bottleneck analysis: {e}")
            return BottleneckResult(False, None, 0.0, "Analysis error") 