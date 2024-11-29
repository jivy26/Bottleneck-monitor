import psutil
import wmi
import logging
import os
import time
from collections import deque
import win32gui
import win32process
import win32con
import pygame
import threading

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ProcessMonitor:
    def __init__(self):
        self.wmi = wmi.WMI()
        self.fps_data = {}
        pygame.init()
        
        self.excluded_processes = {
            'svchost.exe', 'csrss.exe', 'winlogon.exe', 'services.exe',
            'lsass.exe', 'fontdrvhost.exe', 'smss.exe', 'dwm.exe',
            'taskhost.exe', 'explorer.exe', 'sihost.exe', 'taskmgr.exe',
            'devenv.exe', 'chrome.exe', 'firefox.exe', 'msedge.exe',
            'notepad.exe', 'cmd.exe', 'powershell.exe', 'conhost.exe',
            'RuntimeBroker.exe', 'SearchHost.exe', 'ShellExperienceHost.exe',
            'spoolsv.exe', 'wininit.exe', 'wmiprvse.exe', 'SearchIndexer.exe',
            'Registry.exe', 'dllhost.exe', 'Taskmgr.exe', 'mmc.exe',
            'WmiPrvSE.exe', 'ctfmon.exe', 'SearchUI.exe', 'browser_broker.exe',
            'ApplicationFrameHost.exe', 'WindowsTerminal.exe', 'Code.exe',
            'python.exe', 'pythonw.exe', 'wsl.exe', 'bash.exe',
            'nvidia-smi.exe', 'discord.exe', 'slack.exe', 'spotify.exe',
            'mspaint.exe', 'calc.exe', 'wordpad.exe', 'winrar.exe',
            '7zFM.exe', 'vlc.exe', 'zoom.exe', 'skype.exe'
        }
        
        self.game_processes = {
            'Steam.exe', 'EpicGamesLauncher.exe', 'GalaxyClient.exe',
            'Battle.net.exe', 'UbisoftConnect.exe', 'Origin.exe',
            'EADesktop.exe', 'RiotClientServices.exe', 'LeagueClient.exe',
            'GOGGalaxy.exe', 'PlayniteUI.exe', 'GameBarPresenceWriter.exe',
            'UnrealEngine.exe', 'UnrealEditor.exe', 'Unity.exe',
            'CryEngine.exe', 'GameOverlayUI.exe', 'CoherentUI.exe',
            'FortniteClient-Win64-Shipping.exe', 'VALORANT-Win64-Shipping.exe',
            'r5apex.exe', 'GTA5.exe', 'RocketLeague.exe', 'CSGO.exe',
            'Minecraft.exe', 'MinecraftLauncher.exe', 'javaw.exe',
            'League of Legends.exe', 'Overwatch.exe', 'WorldOfWarcraft.exe',
            'destiny2.exe', 'RainbowSix.exe', 'FallGuys_client.exe',
            'DiscordCanary.exe', 'DiscordPTB.exe',
            'GeForceExperience.exe', 'RadeonSoftware.exe',
            'AMDRSServ.exe', 'Overwolf.exe', 'obs64.exe',
            'ShadowPlay.exe', 'MSIAfterburner.exe'
        }
        
        self.running = True
        self.fps_thread = threading.Thread(target=self._fps_monitor_thread, daemon=True)
        self.fps_thread.start()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc.cpu_percent()
            except:
                continue

    def get_running_games(self):
        games = []
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                info = {
                    'pid': process.info['pid'],
                    'name': process.info['name'],
                    'path': process.info['exe']
                }
                
                if info['path'] and info['path'].endswith('.exe'):
                    name = info['name'].lower()
                    path = info['path'].lower()
                    
                    if info['name'] in self.game_processes:
                        games.append(info)
                        continue
                        
                    if info['name'] in self.excluded_processes:
                        continue
                        
                    game_paths = [
                        'steam', 'games', 'epic games',
                        'riot games', 'origin games',
                        'program files\\steam',
                        'program files (x86)\\steam'
                    ]
                    
                    if any(game_path in path for game_path in game_paths):
                        games.append(info)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return sorted(games, key=lambda x: x['name'].lower())

    def _fps_monitor_thread(self):
        clock = pygame.time.Clock()
        while self.running:
            for pid in list(self.fps_data.keys()):
                try:
                    data = self.fps_data[pid]
                    current_time = time.time()
                    data['frame_count'] += 1
                    elapsed_time = current_time - data['last_time']
                    
                    if elapsed_time >= 1.0:
                        data['fps'] = int(data['frame_count'] / elapsed_time)
                        data['frame_count'] = 0
                        data['last_time'] = current_time
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self.fps_data.pop(pid, None)
                    
            clock.tick(240)

    def _calculate_fps(self, process):
        try:
            pid = process.pid
            
            if pid not in self.fps_data:
                self.fps_data[pid] = {
                    'last_time': time.time(),
                    'frame_count': 0,
                    'fps': 0,
                    'hwnd': None,
                    'last_frame_time': time.time(),
                    'frame_times': [],
                    'max_frame_times': 60
                }
            
            def callback(hwnd, extra):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        _, p = win32process.GetWindowThreadProcessId(hwnd)
                        if p == extra['pid']:
                            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                            if style & win32con.WS_VISIBLE:
                                rect = win32gui.GetClientRect(hwnd)
                                if rect[2] > 0 and rect[3] > 0:
                                    extra['hwnd'] = hwnd
                                    return False
                    return True
                except Exception:
                    return True
            
            context = {
                'pid': pid,
                'hwnd': None
            }
            
            try:
                win32gui.EnumWindows(callback, context)
            except Exception as e:
                logger.debug(f"EnumWindows warning (non-critical): {e}")
            
            current_time = time.time()
            data = self.fps_data[pid]
            
            if context['hwnd'] or data['hwnd']:
                data['hwnd'] = context['hwnd'] or data['hwnd']
                
                frame_time = current_time - data['last_frame_time']
                if frame_time > 0:
                    data['frame_times'].append(frame_time)
                    if len(data['frame_times']) > data['max_frame_times']:
                        data['frame_times'].pop(0)
                    
                    avg_frame_time = sum(data['frame_times']) / len(data['frame_times'])
                    
                    if avg_frame_time > 0:
                        instantaneous_fps = 1.0 / avg_frame_time
                        
                        if data['fps'] == 0:
                            data['fps'] = instantaneous_fps
                        else:
                            alpha = 0.1
                            data['fps'] = (alpha * instantaneous_fps) + ((1 - alpha) * data['fps'])
                
                data['last_frame_time'] = current_time
            
            return int(round(data['fps']))
            
        except Exception as e:
            logger.error(f"Error calculating FPS: {e}", exc_info=True)
            return 0

    def get_process_metrics(self, pid):
        try:
            process = psutil.Process(pid)
            
            try:
                cpu_percent = process.cpu_percent(interval=0.1)
            except:
                cpu_percent = process.cpu_percent()
            
            try:
                memory_percent = process.memory_percent()
            except:
                memory_percent = 0
            
            fps = self._calculate_fps(process)
            
            try:
                children = process.children(recursive=True)
                for child in children:
                    try:
                        cpu_percent += child.cpu_percent(interval=0.1)
                    except:
                        continue
            except:
                pass
            
            metrics = {
                'cpu_percent': max(0, min(100, cpu_percent)),
                'memory_percent': max(0, min(100, memory_percent)),
                'fps': fps
            }
            
            logger.debug(f"Process metrics for PID {pid}: {metrics}")
            return metrics
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Could not get process metrics for PID {pid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting process metrics for PID {pid}: {e}")
            return None

    def __del__(self):
        self.running = False
        if hasattr(self, 'fps_thread'):
            self.fps_thread.join(timeout=1.0)
        pygame.quit()