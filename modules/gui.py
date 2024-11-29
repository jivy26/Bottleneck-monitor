from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QComboBox, QPushButton, QLabel, QGridLayout, QScrollArea)
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg
from .process_monitor import ProcessMonitor
from .performance_metrics import PerformanceMetrics
from .graphs import PerformanceGraphs
from .bottleneck_analyzer import BottleneckAnalyzer
from .game_optimizer import GameOptimizer
from .network_monitor import NetworkMonitor
from .input_monitor import InputMonitor
from .frame_analyzer import FrameAnalyzer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Performance Monitor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize all monitors and analyzers
        self.process_monitor = ProcessMonitor()
        self.performance_metrics = PerformanceMetrics()
        self.bottleneck_analyzer = BottleneckAnalyzer()
        self.game_optimizer = GameOptimizer()
        self.network_monitor = NetworkMonitor()
        self.input_monitor = InputMonitor()
        self.frame_analyzer = FrameAnalyzer()
        
        self.setup_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_metrics)
        self.timer.start(500)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Process selection at top
        top_layout = self.setup_top_section()
        main_layout.addLayout(top_layout)
        
        # Create tab widget for different metric views
        tabs = QTabWidget()
        
        # Overview tab
        overview_tab = self.setup_overview_tab()
        tabs.addTab(overview_tab, "Overview")
        
        # Detailed Performance tab
        performance_tab = self.setup_performance_tab()
        tabs.addTab(performance_tab, "Detailed Performance")
        
        # Network tab
        network_tab = self.setup_network_tab()
        tabs.addTab(network_tab, "Network")
        
        # Optimization tab
        optimization_tab = self.setup_optimization_tab()
        tabs.addTab(optimization_tab, "Optimization")
        
        # About tab
        about_tab = self.setup_about_tab()
        tabs.addTab(about_tab, "About")
        
        main_layout.addWidget(tabs)
        
    def setup_top_section(self):
        """Setup the top section with process selector and refresh button"""
        top_layout = QHBoxLayout()
        
        # Process selector dropdown
        self.process_selector = QComboBox()
        self.process_selector.setMinimumWidth(300)
        self.process_selector.currentIndexChanged.connect(self.on_process_changed)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Process List")
        refresh_button.clicked.connect(self.refresh_process_list)
        
        # Add widgets to layout
        top_layout.addWidget(QLabel("Select Process:"))
        top_layout.addWidget(self.process_selector)
        top_layout.addWidget(refresh_button)
        top_layout.addStretch()
        
        # Initial process list population
        self.refresh_process_list()
        
        return top_layout
        
    def refresh_process_list(self):
        """Refresh the list of running processes"""
        current_pid = self.process_selector.currentData()
        
        # Get running games
        games = self.process_monitor.get_running_games()
        
        # Clear and repopulate the combo box
        self.process_selector.clear()
        for game in games:
            self.process_selector.addItem(game['name'], game['pid'])
            
        if current_pid:
            index = self.process_selector.findData(current_pid)
            if index >= 0:
                self.process_selector.setCurrentIndex(index)
        
    def on_process_changed(self, index):
        """Handle process selection change"""
        if hasattr(self, 'frame_analyzer'):
            self.frame_analyzer.frame_times.clear()
        
    def setup_overview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        metrics_layout = QGridLayout()
        self.metrics_labels = {
            'fps': QLabel("FPS: --"),
            'cpu': QLabel("CPU Usage: --"),
            'gpu': QLabel("GPU Usage: --"),
            'ram': QLabel("RAM Usage: --"),
            'cpu_temp': QLabel("CPU Temp: --"),
            'gpu_temp': QLabel("GPU Temp: --"),
            'bottleneck': QLabel("Bottleneck: --"),
            'frame_time': QLabel("Frame Time: --"),
            'frame_pacing': QLabel("Frame Pacing: --"),
            'input_lag': QLabel("Input Lag: --")
        }
        
        for label in self.metrics_labels.values():
            label.setStyleSheet("QLabel { color: white; font-size: 14px; }")
            
        row = 0
        col = 0
        for key, label in self.metrics_labels.items():
            metrics_layout.addWidget(label, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        self.graphs = PerformanceGraphs()
        
        layout.addLayout(metrics_layout)
        layout.addWidget(self.graphs)
        return widget
        
    def setup_performance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)
        panel_layout = QVBoxLayout(panel)
        
        # Frame Time Analysis Section
        frame_time_group = QWidget()
        frame_time_layout = QVBoxLayout(frame_time_group)
        
        # Title for the section
        title = QLabel("Frame Time Analysis")
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 5px;
                border-bottom: 1px solid #333333;
            }
        """)
        frame_time_layout.addWidget(title)
        
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)
        
        self.frame_metrics = {
            'avg_frame_time': {
                'label': QLabel("Average Frame Time"),
                'value': QLabel("--"),
                'unit': "ms"
            },
            '1%_low': {
                'label': QLabel("1% Low"),
                'value': QLabel("--"),
                'unit': "ms"
            },
            '0.1%_low': {
                'label': QLabel("0.1% Low"),
                'value': QLabel("--"),
                'unit': "ms"
            },
            'stutters': {
                'label': QLabel("Stutters Detected"),
                'value': QLabel("--"),
                'unit': ""
            },
            'frame_variance': {
                'label': QLabel("Frame Time Variance"),
                'value': QLabel("--"),
                'unit': "ms²"
            }
        }
        
        row = 0
        for metric_key, metric_data in self.frame_metrics.items():
            container = QWidget()
            container.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            container_layout = QHBoxLayout(container)
            
            metric_data['label'].setStyleSheet("""
                QLabel {
                    color: #aaaaaa;
                    font-size: 14px;
                }
            """)
            
            # Style the value
            metric_data['value'].setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            
            # Add to container
            container_layout.addWidget(metric_data['label'])
            container_layout.addWidget(metric_data['value'])
            container_layout.addStretch()
            
            # Add container to grid
            metrics_grid.addWidget(container, row, 0)
            row += 1
        
        frame_time_layout.addLayout(metrics_grid)
        panel_layout.addWidget(frame_time_group)
        
        # Add performance tips section
        tips_widget = QWidget()
        tips_layout = QVBoxLayout(tips_widget)
        
        tips_title = QLabel("Performance Tips")
        tips_title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 5px;
                border-bottom: 1px solid #333333;
            }
        """)
        tips_layout.addWidget(tips_title)
        
        tips_text = QLabel(
            "• Lower frame time is better (16.7ms = 60 FPS)\n"
            "• 1% and 0.1% lows indicate stutter severity\n"
            "• High frame variance can indicate inconsistent performance\n"
            "• Monitor these values while gaming to identify issues"
        )
        tips_text.setStyleSheet("""
            QLabel {
                color: #bbbbbb;
                font-size: 14px;
                padding: 10px;
            }
        """)
        tips_text.setWordWrap(True)
        tips_layout.addWidget(tips_text)
        
        panel_layout.addWidget(tips_widget)
        panel_layout.addStretch()
        
        # Add panel to main layout
        layout.addWidget(panel)
        
        return widget
        
    def setup_network_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a dark background panel
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)
        panel_layout = QVBoxLayout(panel)
        
        # Network Metrics Section
        network_group = QWidget()
        network_layout = QVBoxLayout(network_group)
        
        # Title
        title = QLabel("Network Analysis")
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 5px;
                border-bottom: 1px solid #333333;
            }
        """)
        network_layout.addWidget(title)
        
        # Grid for metrics
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)
        
        self.network_metrics = {
            'bytes_sent': {
                'label': QLabel("Bytes Sent"),
                'value': QLabel("--")
            },
            'bytes_recv': {
                'label': QLabel("Bytes Received"),
                'value': QLabel("--")
            },
            'connections': {
                'label': QLabel("Active Connections"),
                'value': QLabel("--")
            }
        }
        
        # Add metrics to grid
        row = 0
        for metric_key, metric_data in self.network_metrics.items():
            # Container for each metric
            container = QWidget()
            container.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            container_layout = QHBoxLayout(container)
            
            # Style the label and value
            metric_data['label'].setStyleSheet("QLabel { color: #aaaaaa; font-size: 14px; }")
            metric_data['value'].setStyleSheet("QLabel { color: #ffffff; font-size: 16px; font-weight: bold; }")
            
            # Add to container
            container_layout.addWidget(metric_data['label'])
            container_layout.addWidget(metric_data['value'])
            container_layout.addStretch()
            
            # Add container to grid
            metrics_grid.addWidget(container, row, 0)
            row += 1
        
        network_layout.addLayout(metrics_grid)
        
        # Server Connections Section
        servers_title = QLabel("Connected Servers")
        servers_title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 5px;
                margin-top: 20px;
                border-bottom: 1px solid #333333;
            }
        """)
        network_layout.addWidget(servers_title)
        
        self.servers_list = QLabel("No active connections")
        self.servers_list.setStyleSheet("""
            QLabel {
                color: #bbbbbb;
                font-size: 14px;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
        """)
        self.servers_list.setWordWrap(True)
        network_layout.addWidget(self.servers_list)
        
        panel_layout.addWidget(network_group)
        layout.addWidget(panel)
        return widget
        
    def setup_optimization_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a dark background panel
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)
        panel_layout = QVBoxLayout(panel)
        
        # Optimization Tips Section
        tips_group = QWidget()
        tips_layout = QVBoxLayout(tips_group)
        
        # Title
        title = QLabel("Optimization Recommendations")
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 5px;
                border-bottom: 1px solid #333333;
            }
        """)
        tips_layout.addWidget(title)
        
        # Tips container
        tips_container = QWidget()
        tips_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        tips_container_layout = QVBoxLayout(tips_container)
        
        self.optimization_labels = []
        for _ in range(10):
            label = QLabel()
            label.setWordWrap(True)
            label.setStyleSheet("""
                QLabel {
                    color: #bbbbbb;
                    font-size: 14px;
                    padding: 5px;
                }
            """)
            self.optimization_labels.append(label)
            tips_container_layout.addWidget(label)
        
        tips_layout.addWidget(tips_container)
        panel_layout.addWidget(tips_group)
        
        # Add explanation section
        explanation = QLabel(
            "• Tips are updated in real-time based on performance metrics\n"
            "• Recommendations are tailored to your specific hardware\n"
            "• Some optimizations may require system or game settings changes\n"
            "• Performance impact may vary depending on your setup"
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                padding: 15px;
                margin-top: 20px;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
        """)
        explanation.setWordWrap(True)
        panel_layout.addWidget(explanation)
        
        layout.addWidget(panel)
        return widget
        
    def setup_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create a dark background panel
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)
        panel_layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("About PC Performance Monitor")
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 5px;
                border-bottom: 1px solid #333333;
            }
        """)
        panel_layout.addWidget(title)
        
        # Version info container
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_container)
        
        version_label = QLabel("Version: 1.0")
        release_label = QLabel("Release Date: November 29, 2024")
        url_label = QLabel('<a href="https://github.com/jivy26/pcmonitor">https://github.com/jivy26/pcmonitor</a>')
        url_label.setOpenExternalLinks(True)
        
        for label in [version_label, release_label, url_label]:
            label.setStyleSheet("""
                QLabel {
                    color: #bbbbbb;
                    font-size: 14px;
                    padding: 5px;
                }
                QLabel a {
                    color: #00aaff;
                    text-decoration: none;
                }
                QLabel a:hover {
                    text-decoration: underline;
                }
            """)
        
        info_layout.addWidget(version_label)
        info_layout.addWidget(release_label)
        info_layout.addWidget(url_label)
        info_layout.addStretch()
        
        panel_layout.addWidget(info_container)
        panel_layout.addStretch()
        
        layout.addWidget(panel)
        return widget
        
    def update_all_metrics(self):
        if not self.process_selector.currentData():
            return
            
        pid = self.process_selector.currentData()
        process_name = self.process_selector.currentText()
        
        # Get all metrics
        process_metrics = self.process_monitor.get_process_metrics(pid)
        system_metrics = self.performance_metrics.get_system_metrics()
        
        if process_metrics and system_metrics:
            # Update graphs first (preserve working functionality)
            self.graphs.update_graphs(process_metrics, system_metrics)
            
            # Update basic metrics
            self.update_basic_metrics(process_metrics, system_metrics)
            
            # Calculate and update frame analysis
            if process_metrics['fps'] > 0:
                frame_time = 1000.0 / process_metrics['fps']  # Convert to milliseconds
                frame_analysis = self.frame_analyzer.analyze_frame_times(frame_time)
                self.update_frame_metrics(frame_analysis)
            
            # Update network metrics if available
            network_metrics = self.network_monitor.get_process_network_metrics(pid)
            if network_metrics:
                self.update_network_metrics(network_metrics)
            
            # Update optimization tips
            tips = self.game_optimizer.get_optimization_tips(process_name, process_metrics)
            self.update_optimization_tips(tips)
            
            # Update input lag if window handle available
            if hasattr(process_metrics, 'hwnd'):
                input_lag = self.input_monitor.measure_input_lag(process_metrics['hwnd'])
                if input_lag:
                    self.metrics_labels['input_lag'].setText(f"Input Lag: {input_lag:.1f}ms")
            
    def update_basic_metrics(self, process_metrics, system_metrics):
        """Update the basic metrics display"""
        try:
            # Update FPS
            self.metrics_labels['fps'].setText(f"FPS: {process_metrics['fps']}")
            
            # Update CPU metrics
            cpu_info = system_metrics['cpu']
            self.metrics_labels['cpu'].setText(f"CPU Usage: {process_metrics['cpu_percent']:.1f}%")
            self.metrics_labels['cpu_temp'].setText(f"CPU Temp: {cpu_info['temperature']:.1f}°C")
            
            # Update GPU metrics
            gpu_info = system_metrics.get('gpu', {})
            self.metrics_labels['gpu'].setText(f"GPU Usage: {gpu_info.get('utilization', 0):.1f}%")
            self.metrics_labels['gpu_temp'].setText(f"GPU Temp: {gpu_info.get('temperature', 0):.1f}°C")
            
            # Update RAM usage - Fix memory display
            memory_info = system_metrics.get('memory', {})
            memory_percent = memory_info.get('percent', process_metrics['memory_percent'])
            self.metrics_labels['ram'].setText(f"RAM Usage: {memory_percent:.1f}%")
            
            # Calculate frame time from FPS
            if process_metrics['fps'] > 0:
                frame_time = 1000.0 / process_metrics['fps']  # Convert to milliseconds
                self.metrics_labels['frame_time'].setText(f"Frame Time: {frame_time:.1f}ms")
            else:
                self.metrics_labels['frame_time'].setText("Frame Time: --")
            
            # Get bottleneck analysis
            bottleneck = self.bottleneck_analyzer.analyze(process_metrics, system_metrics)
            if bottleneck.exists:
                self.metrics_labels['bottleneck'].setText(
                    f"Bottleneck: {bottleneck.component} ({bottleneck.severity*100:.0f}%)"
                )
                # Set red color for bottleneck warning
                self.metrics_labels['bottleneck'].setStyleSheet(
                    "QLabel { color: #ff4444; font-size: 14px; font-weight: bold; }"
                )
            else:
                self.metrics_labels['bottleneck'].setText("Bottleneck: None")
                # Set green color for no bottleneck
                self.metrics_labels['bottleneck'].setStyleSheet(
                    "QLabel { color: #44ff44; font-size: 14px; }"
                )
            
            # Update frame pacing status
            if hasattr(process_metrics, 'frame_time'):
                frame_analysis = self.frame_analyzer.analyze_frame_times(process_metrics['frame_time'])
                self.metrics_labels['frame_pacing'].setText(f"Frame Pacing: {frame_analysis['frame_pacing']}")
            
        except Exception as e:
            logger.error(f"Error updating basic metrics: {e}")
        
    def update_frame_metrics(self, frame_analysis):
        """Update the frame metrics display"""
        try:
            # Update values with color coding
            for key, metric_data in self.frame_metrics.items():
                if key in frame_analysis:
                    value = frame_analysis[key]
                    
                    # Format value based on metric type
                    if key == 'stutters':
                        formatted_value = str(int(value))
                        # Color code based on stutter count
                        if value == 0:
                            color = "#44ff44"  # Green
                        elif value < 5:
                            color = "#ffff44"  # Yellow
                        else:
                            color = "#ff4444"  # Red
                    else:
                        formatted_value = f"{value:.2f}{metric_data['unit']}"
                        # Color code based on frame time thresholds
                        if key in ['avg_frame_time', '1%_low', '0.1%_low']:
                            if value < 16.7:  # Better than 60 FPS
                                color = "#44ff44"  # Green
                            elif value < 33.3:  # Better than 30 FPS
                                color = "#ffff44"  # Yellow
                            else:
                                color = "#ff4444"  # Red
                        else:
                            color = "#ffffff"  # Default white
                    
                    metric_data['value'].setText(formatted_value)
                    metric_data['value'].setStyleSheet(f"""
                        QLabel {{
                            color: {color};
                            font-size: 16px;
                            font-weight: bold;
                        }}
                    """)
                    
        except Exception as e:
            logger.error(f"Error updating frame metrics: {e}")
        
    def update_network_metrics(self, network_metrics):
        if network_metrics:
            # Update basic metrics
            self.network_metrics['bytes_sent']['value'].setText(f"{network_metrics['bytes_sent']/1024:.1f} KB/s")
            self.network_metrics['bytes_recv']['value'].setText(f"{network_metrics['bytes_recv']/1024:.1f} KB/s")
            self.network_metrics['connections']['value'].setText(str(network_metrics['active_connections']))
            
            # Update server list
            servers = network_metrics.get('servers', [])
            if servers:
                server_text = "\n".join([f"• {s['hostname']} ({s['ip']}:{s['port']})" for s in servers])
                self.servers_list.setText(server_text)
            else:
                self.servers_list.setText("No active connections")
        
    def update_optimization_tips(self, tips):
        # Clear old tips
        for label in self.optimization_labels:
            label.setText("")
            
        # Add new tips
        for i, tip in enumerate(tips):
            if i < len(self.optimization_labels):
                self.optimization_labels[i].setText(f"• {tip}")