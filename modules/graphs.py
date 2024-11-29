from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
import pyqtgraph as pg
import numpy as np

class PerformanceGraphs(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_graphs()
        
    def setup_graphs(self):
        layout = QGridLayout(self)
        layout.setSpacing(10)
        
        self.cpu_plot = self.create_plot("CPU Usage (%)")
        self.memory_plot = self.create_plot("Memory Usage (%)")
        self.gpu_plot = self.create_plot("GPU Usage (%)")
        self.temperature_plot = self.create_plot("Temperature (°C)")
        
        self.data_length = 100
        self.times = np.linspace(0, self.data_length, self.data_length)
        self.cpu_data = np.zeros(self.data_length)
        self.memory_data = np.zeros(self.data_length)
        self.gpu_data = np.zeros(self.data_length)
        self.temp_data = np.zeros(self.data_length)
        
        self.cpu_curve = self.cpu_plot.plot(self.times, self.cpu_data, pen='g')
        self.memory_curve = self.memory_plot.plot(self.times, self.memory_data, pen='r')
        self.gpu_curve = self.gpu_plot.plot(self.times, self.gpu_data, pen='b')
        self.temp_curve = self.temperature_plot.plot(self.times, self.temp_data, pen='m')
        
        layout.addWidget(self.cpu_plot, 0, 0)
        layout.addWidget(self.memory_plot, 0, 1)
        layout.addWidget(self.gpu_plot, 1, 0)
        layout.addWidget(self.temperature_plot, 1, 1)
        
    def create_plot(self, title):
        plot = pg.PlotWidget()
        plot.setBackground('#2d2d2d')
        plot.setTitle(title, color='#ffffff')
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('left', 'Value', color='#ffffff')
        plot.setLabel('bottom', 'Time (s)', color='#ffffff')
        
        plot.getAxis('left').setPen('w')
        plot.getAxis('bottom').setPen('w')
        
        plot.setYRange(0, 100)
        
        return plot
        
    def update_graphs(self, process_metrics, system_metrics):
        self.cpu_data[:-1] = self.cpu_data[1:]
        self.memory_data[:-1] = self.memory_data[1:]
        self.gpu_data[:-1] = self.gpu_data[1:]
        self.temp_data[:-1] = self.temp_data[1:]
        
        self.cpu_data[-1] = process_metrics['cpu_percent']
        self.memory_data[-1] = process_metrics['memory_percent']
        
        gpu_info = system_metrics.get('gpu', {})
        self.gpu_data[-1] = gpu_info.get('utilization', 0)
        
        cpu_info = system_metrics.get('cpu', {})
        self.temp_data[-1] = cpu_info.get('temperature', 0)
        
        self.cpu_curve.setData(self.times, self.cpu_data)
        self.memory_curve.setData(self.times, self.memory_data)
        self.gpu_curve.setData(self.times, self.gpu_data)
        self.temp_curve.setData(self.times, self.temp_data) 