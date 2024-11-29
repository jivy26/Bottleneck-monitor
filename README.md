# PC Performance Monitor

A real-time performance monitoring tool for Windows that helps detect bottlenecks and optimize gaming performance. Monitor CPU, GPU, RAM usage, FPS, frame times, and network performance in real-time with a modern dark-themed interface.

![PC Performance Monitor Screenshot](resources/screenshot.png)

## Repository

https://github.com/YOUR_USERNAME/pc-performance-monitor

## Features

### Real-time Performance Monitoring
- CPU & GPU Usage and Temperature
- RAM Usage and Management
- FPS Counter with Frame Time Analysis
- Input Lag Detection
- Network Performance Tracking

### Advanced Analytics
- Automatic Bottleneck Detection
- Frame Time Analysis
  - 1% and 0.1% Low FPS
  - Frame Pacing Quality
  - Stutter Detection
- Network Performance
  - Bandwidth Monitoring
  - Active Connections
  - Server Details

### Game Optimization
- Real-time Performance Tips
- Game-specific Recommendations
- Hardware-specific Suggestions
- System Configuration Advice

## Installation

### Prerequisites
- Windows 10/11 64-bit
- Python 3.8 or higher
- Administrator privileges (for hardware monitoring)
- GPU drivers: NVIDIA (470.0+) or AMD (21.5.2+)

### Build Instructions
1. Clone the repository:
```bash
git clone https://github.com/jivy26/pcmonitor.git
```
2. Navigate to the project directory:
```bash
cd pcmonitor
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the application:
```bash
python main.py
```

## Usage
- Run the application as administrator for best performance monitoring
- Select the game process from the dropdown menu
- View real-time performance metrics and analytics
- Receive game optimization tips and suggestions

## Configuration
- The application saves the last selected process ID to `last_session.json` for faster startup
- You can manually edit this file to change the last selected process
