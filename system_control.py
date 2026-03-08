"""
🖥️ SARA - System Control Module (Secure & Robust)
=================================================
Control avanzado del sistema operativo Windows.
Mejoras:
- Uso de psutil para gestión de procesos (más rápido y seguro que taskkill).
- Ejecución de comandos sin shell=True (evita inyección).
- Manejo de errores granular.
"""

import os
import logging
import subprocess
import ctypes
from ctypes import cast, POINTER, wintypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Union

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SYSTEM - %(levelname)s - %(message)s')
logger = logging.getLogger("SYSTEM")

# Importaciones de terceros con flags de estado
LIBRARIES_OK = True
try:
    import psutil
    import pyautogui
    import screen_brightness_control as sbc
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError as e:
    logger.critical(f"❌ Faltan librerías necesarias: {e}")
    LIBRARIES_OK = False

# Constantes de Windows
SC_MONITORPOWER = 0xF170
WM_SYSCOMMAND = 0x0112
MONITOR_OFF = 2
WM_CLOSE = 0x0010

class SystemControl:
    def __init__(self):
        if not LIBRARIES_OK:
            logger.warning("⚠️ SystemControl operando en modo limitado (faltan librerías).")
        
        self.volume = self._get_volume_interface()
        self.base_dir = Path(__file__).parent.absolute()

    def _get_volume_interface(self):
        """Inicializa la interfaz de audio de Windows."""
        if not LIBRARIES_OK: return None
        try:
            device = AudioUtilities.GetSpeakers()
            if hasattr(device, 'EndpointVolume'):
                return device.EndpointVolume
            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.error(f"Error audio interface: {e}")
            return None

    # ==========================================
    # AUDIO Y BRILLO
    # ==========================================

    def set_volume(self, level: int) -> str:
        if not self.volume: return "Error: Audio no disponible."
        try:
            level = max(0, min(100, level))
            scalar = level / 100.0
            self.volume.SetMasterVolumeLevelScalar(scalar, None)
            return f"🔊 Volumen ajustado al {level}%."
        except Exception as e:
            return f"❌ Error volumen: {e}"

    def get_volume(self) -> int:
        if not self.volume: return 0
        try:
            return int(self.volume.GetMasterVolumeLevelScalar() * 100)
        except: return 0

    def adjust_volume(self, change: int) -> str:
        current = self.get_volume()
        return self.set_volume(current + change)

    def mute_volume(self) -> str:
        if not self.volume: return "Error: Audio no disponible."
        try:
            current_mute = self.volume.GetMute()
            self.volume.SetMute(not current_mute, None)
            state = "desactivado" if current_mute else "activado"
            return f"🔇 Silencio {state}."
        except Exception as e:
            return f"❌ Error mute: {e}"

    def set_brightness(self, level: int) -> str:
        if not LIBRARIES_OK: return "Librería sbc no instalada."
        try:
            level = max(0, min(100, level))
            sbc.set_brightness(level)
            return f"☀️ Brillo ajustado al {level}%."
        except Exception as e:
            logger.error(f"Error brillo: {e}")
            return "No pude ajustar el brillo (quizás no es monitor compatible)."

    # ==========================================
    # CONTROLES DE MEDIOS Y PANTALLA
    # ==========================================

    def media_play_pause(self) -> str:
        if LIBRARIES_OK: pyautogui.press('playpause')
        return "⏯️ Media: Play/Pause"

    def media_next(self) -> str:
        if LIBRARIES_OK: pyautogui.press('nexttrack')
        return "⏭️ Media: Siguiente"

    def media_prev(self) -> str:
        if LIBRARIES_OK: pyautogui.press('prevtrack')
        return "⏮️ Media: Anterior"

    def lock_screen(self) -> str:
        try:
            ctypes.windll.user32.LockWorkStation()
            return "🔒 Pantalla bloqueada"
        except Exception as e:
            return f"❌ Error bloqueo: {e}"

    def turn_off_screen(self) -> str:
        try:
            # Pequeño delay para que no se despierte al soltar teclas
            import time
            time.sleep(0.5) 
            ctypes.windll.user32.SendMessageW(
                ctypes.windll.user32.GetForegroundWindow(),
                WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF
            )
            return "🌑 Apagando pantalla..."
        except Exception as e:
            return f"❌ Error apagando pantalla: {e}"

    # ==========================================
    # GESTIÓN DE PROCESOS (OPTIMIZADO CON PSUTIL)
    # ==========================================

    def kill_process(self, process_name: str) -> str:
        """Mata un proceso de forma nativa y segura."""
        if not LIBRARIES_OK: return "Falta librería psutil."
        
        # Limpieza nombre (quitar .exe si usuario lo puso)
        target = process_name.lower().replace(".exe", "")
        killed_count = 0
        
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    # Comparación flexible
                    if target in proc.info['name'].lower():
                        proc.kill()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed_count > 0:
                return f"✅ Se terminaron {killed_count} procesos '{target}'."
            return f"⚠️ No encontré procesos activos con el nombre '{target}'."
            
        except Exception as e:
            return f"❌ Error matando proceso: {e}"

    def get_heavy_processes(self, limit: int = 5) -> str:
        """Top procesos consumidores de RAM."""
        if not LIBRARIES_OK: return "Falta psutil."
        try:
            procs = []
            for p in psutil.process_iter(['name', 'memory_info']):
                try:
                    mem = p.info['memory_info']
                    if mem:
                        procs.append({
                            'name': p.info['name'],
                            'rss': mem.rss
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Ordenar por uso de RAM (RSS)
            procs.sort(key=lambda x: x['rss'], reverse=True)
            
            reporte = "🚨 TOP CONSUMO RAM:\n"
            for p in procs[:limit]:
                mb = round(p['rss'] / (1024 * 1024), 1)
                reporte += f"• {p['name']}: {mb} MB\n"
            return reporte
            
        except Exception as e:
            return f"❌ Error leyendo procesos: {e}"

    # ==========================================
    # SISTEMA (SEGURO SIN SHELL=TRUE)
    # ==========================================

    def shutdown_system(self, minutes: int = 0) -> str:
        """Apagado seguro."""
        seconds = str(int(minutes * 60))
        try:
            # shell=False evita inyección de comandos
            subprocess.run(["shutdown", "/s", "/t", seconds], shell=False)
            
            if minutes > 0:
                return f"🕒 Apagado programado en {minutes} min."
            return "👋 Apagando sistema..."
        except Exception as e:
            return f"❌ Error shutdown: {e}"

    def restart_system(self, minutes: int = 0) -> str:
        """Reinicio seguro."""
        seconds = str(int(minutes * 60))
        try:
            subprocess.run(["shutdown", "/r", "/t", seconds], shell=False)
            
            if minutes > 0:
                return f"🔄 Reinicio programado en {minutes} min."
            return "🔄 Reiniciando..."
        except Exception as e:
            return f"❌ Error restart: {e}"

    def cancel_shutdown(self) -> str:
        try:
            subprocess.run(["shutdown", "/a"], shell=False)
            return "✅ Apagado cancelado."
        except:
            return "ℹ️ No había temporizador."

    def empty_recycle_bin(self) -> str:
        try:
            SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
            # Flags: 1=NoConfirm, 2=NoProgress, 4=NoSound
            result = SHEmptyRecycleBin(None, None, 7)
            if result == 0: return "🗑️ Papelera vaciada."
            if result == -2147418113: return "ℹ️ Ya estaba vacía."
            return f"⚠️ Código error: {result}"
        except Exception as e:
            return f"❌ Error papelera: {e}"

    def minimize_all_windows(self) -> str:
        if LIBRARIES_OK: pyautogui.hotkey('win', 'd')
        return "🖥️ Escritorio."

    def maximize_window(self) -> str:
        if LIBRARIES_OK: pyautogui.hotkey('win', 'up')
        return "Ventana maximizada."

    def clean_temp_files(self) -> str:
        """Limpieza de temporales optimizada."""
        temp_dir = os.environ.get('TEMP')
        if not temp_dir: return "❌ No existe variable TEMP."
        
        deleted_files = 0
        deleted_size = 0
        
        try:
            with os.scandir(temp_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        try:
                            size = entry.stat().st_size
                            os.remove(entry.path)
                            deleted_files += 1
                            deleted_size += size
                        except (PermissionError, OSError):
                            continue # Archivo en uso, ignorar
            
            mb = round(deleted_size / (1024*1024), 2)
            return f"🧹 Limpieza: {deleted_files} archivos ({mb} MB)."
        except Exception as e:
            return f"❌ Error limpieza: {e}"

    def close_window_by_title(self, partial_title: str) -> str:
        """Cierra ventanas por título (WinAPI)."""
        user32 = ctypes.windll.user32
        found_count = 0
        
        def check_window(hwnd, _):
            nonlocal found_count
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                if user32.IsWindowVisible(hwnd) and partial_title.lower() in title.lower():
                    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                    found_count += 1
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(check_window), 0)
        
        if found_count > 0:
            return f"✅ Cerradas {found_count} ventanas con '{partial_title}'."
        return f"ℹ️ No encontré ventanas '{partial_title}'."

    # ==========================================
    # DIAGNÓSTICO DE RED
    # ==========================================

    def get_network_status(self) -> str:
        """Diagnóstico completo de red: conexión, IP, latencia y tipo."""
        try:
            import socket
            import time
            
            # 1. Obtener información local
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # 2. Verificar Internet con ping a Google DNS (8.8.8.8)
            param = '-n' if os.name == 'nt' else '-c'
            start_time = time.time()
            
            response = subprocess.call(
                ['ping', param, '1', '8.8.8.8'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # 3. Determinar estado de conexión
            if response == 0:
                # Evaluar calidad de latencia
                if latency_ms < 50:
                    status = "✅ Excelente"
                    quality = "🟢"
                elif latency_ms < 150:
                    status = "✅ Buena"
                    quality = "🟡"
                elif latency_ms < 300:
                    status = "⚠️ Lenta"
                    quality = "🟠"
                else:
                    status = "⚠️ Muy Lenta"
                    quality = "🔴"
                
                return f"{quality} {status} ({latency_ms}ms) | IP: {local_ip} | Host: {hostname}"
            else:
                return f"❌ Sin Internet | IP Local: {local_ip} | Host: {hostname}"
                
        except Exception as e:
            logger.error(f"Error diagnóstico de red: {e}")
            return f"❌ Error de red: {e}"

    def get_network_latency(self) -> Optional[int]:
        """
        Retorna latencia en ms (para uso interno).
        Útil para que brain.py detecte si un error fue por red lenta.
        """
        try:
            import time
            param = '-n' if os.name == 'nt' else '-c'
            start = time.time()
            
            response = subprocess.call(
                ['ping', param, '1', '8.8.8.8'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            
            if response == 0:
                return int((time.time() - start) * 1000)
            return None  # Sin conexión
        except:
            return None

    def check_internet(self) -> bool:
        """Verificación rápida de Internet (True/False)."""
        try:
            param = '-n' if os.name == 'nt' else '-c'
            response = subprocess.call(
                ['ping', param, '1', '8.8.8.8'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
                timeout=5
            )
            return response == 0
        except:
            return False

# --- PRUEBAS ---
if __name__ == "__main__":
    sys = SystemControl()
    print("--- TEST SYSTEM CONTROL ---\n")
    
    # Test diagnóstico de red
    print("📡 DIAGNÓSTICO DE RED:")
    print(sys.get_network_status())
    print()
    
    # Test procesos pesados
    print(sys.get_heavy_processes(3))
    
    # Otros tests (comentados)
    # print(sys.set_volume(20))
    # print(sys.clean_temp_files())