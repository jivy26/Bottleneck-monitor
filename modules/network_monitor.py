import psutil
import socket
from typing import Dict, Optional

class NetworkMonitor:
    def __init__(self):
        self.last_bytes = None
        self.connections = {}
        
    def get_process_network_metrics(self, pid: int) -> Dict:
        try:
            process = psutil.Process(pid)
            connections = process.connections()
            
            net_io = process.io_counters()
            current_bytes = (net_io.read_bytes, net_io.write_bytes)
            
            if self.last_bytes:
                bytes_sent = current_bytes[1] - self.last_bytes[1]
                bytes_recv = current_bytes[0] - self.last_bytes[0]
            else:
                bytes_sent = bytes_recv = 0
                
            self.last_bytes = current_bytes
            
            servers = []
            for conn in connections:
                if conn.raddr:
                    try:
                        hostname = socket.gethostbyaddr(conn.raddr.ip)[0]
                        servers.append({
                            'ip': conn.raddr.ip,
                            'port': conn.raddr.port,
                            'hostname': hostname
                        })
                    except:
                        continue
            
            return {
                'bytes_sent': bytes_sent,
                'bytes_recv': bytes_recv,
                'active_connections': len(connections),
                'servers': servers
            }
        except:
            return {} 