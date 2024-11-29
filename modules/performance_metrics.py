import psutil
import wmi
import pythoncom
import logging
import subprocess
import os
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class PerformanceMetrics:
    def __init__(self):
        pythoncom.CoInitialize()
        self.wmi = wmi.WMI()
        self.nvidia_smi_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 
                                          'System32', 'nvidia-smi.exe')
        self.has_nvidia = os.path.exists(self.nvidia_smi_path)
        if self.has_nvidia:
            logger.info("NVIDIA GPU monitoring initialized successfully")
        else:
            logger.warning("NVIDIA SMI not found at expected path")
    
    def get_system_metrics(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=0)
            memory = psutil.virtual_memory()
            gpu_info = self._get_gpu_metrics()
            cpu_temp = self._get_cpu_temperature()
            
            metrics = {
                'cpu': {
                    'utilization': cpu_percent,
                    'temperature': cpu_temp if cpu_temp is not None else 0
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'gpu': gpu_info,
                'storage': self._get_storage_metrics()
            }
            
            logger.debug(f"System metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return None

    def _get_cpu_temperature(self):
        try:
            try:
                w = wmi.WMI(namespace="root/OpenHardwareMonitor")
                temps = w.Sensor(SensorType='Temperature')
                for temp in temps:
                    if 'cpu' in temp.Name.lower() or 'package' in temp.Name.lower():
                        return temp.Value
            except Exception as e:
                logger.debug(f"OpenHardwareMonitor method failed: {e}")

            try:
                w = wmi.WMI(namespace="root/WMI")
                temps = w.MSAcpi_ThermalZoneTemperature()
                if temps:
                    return (temps[0].CurrentTemperature / 10.0) - 273.15
            except Exception as e:
                logger.debug(f"MSI Afterburner method failed: {e}")

            try:
                w = wmi.WMI(namespace="root/CIMV2")
                temps = w.Win32_PerfFormattedData_Counters_ThermalZoneInformation()
                if temps:
                    return float(temps[0].Temperature)
            except Exception as e:
                logger.debug(f"Win32_PerfFormattedData method failed: {e}")

            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for source in ['coretemp', 'k10temp', 'zenpower', 'acpitz']:
                            if source in temps:
                                return temps[source][0].current
            except Exception as e:
                logger.debug(f"psutil sensors method failed: {e}")

            try:
                w = wmi.WMI(namespace="root/speedfan")
                temps = w.Sensor(SensorType='Temperature')
                if temps:
                    return temps[0].Value
            except Exception as e:
                logger.debug(f"Speedfan method failed: {e}")

            logger.warning("No CPU temperature sources available")
            return None

        except Exception as e:
            logger.error(f"Error getting CPU temperature: {e}")
            return None

    def _get_gpu_metrics(self):
        if self.has_nvidia:
            try:
                cmd = [self.nvidia_smi_path, 
                      "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total", 
                      "--format=csv,noheader,nounits"]
                
                output = subprocess.check_output(cmd).decode('utf-8').strip()
                util, temp, mem_used, mem_total = map(float, output.split(','))
                
                mem_percent = (mem_used / mem_total) * 100 if mem_total > 0 else 0
                
                metrics = {
                    'utilization': util,
                    'temperature': temp,
                    'memory_used': mem_used,
                    'memory_total': mem_total,
                    'memory_percent': mem_percent
                }
                logger.debug(f"NVIDIA GPU metrics: {metrics}")
                return metrics
            except Exception as e:
                logger.error(f"Error getting NVIDIA GPU metrics: {e}")
                return self._get_wmi_gpu_metrics()
        return self._get_wmi_gpu_metrics()

    def _get_wmi_gpu_metrics(self):
        try:
            gpu = self.wmi.Win32_VideoController()[0]
            metrics = {
                'name': gpu.Name,
                'memory': gpu.AdapterRAM if hasattr(gpu, 'AdapterRAM') else None,
                'driver_version': gpu.DriverVersion,
                'utilization': 0,
                'temperature': 0
            }
            logger.debug(f"WMI GPU metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"WMI GPU error: {e}")
            return {
                'utilization': 0,
                'temperature': 0
            }
            
    def _get_storage_metrics(self):
        disks = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks[partition.device] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except:
                continue
        return disks