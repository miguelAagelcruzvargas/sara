import logging
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import pyautogui

class SystemControl:
    def __init__(self):
        self.volume = self._get_volume_interface()

    def _get_volume_interface(self):
        try:
            device = AudioUtilities.GetSpeakers()
            # Newer pycaw versions expose EndpointVolume directly
            if hasattr(device, 'EndpointVolume'):
                return device.EndpointVolume
                
            # Fallback for older (standard) usage if needed
            interface = device.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logging.error(f"Error initializing audio interface: {e}")
            return None

    def set_volume(self, level: int):
        """Sets the master volume to a specific percentage (0-100)."""
        if not self.volume: return "Error: Audio interface not available."
        
        # Ensure level is between 0 and 100
        level = max(0, min(100, level))
        
        try:
            # Pycaw uses scalar 0.0 to 1.0
            scalar = level / 100.0
            self.volume.SetMasterVolumeLevelScalar(scalar, None)
            return f"Volumen ajustado al {level}%."
        except Exception as e:
            return f"Error ajustando volumen: {e}"

    def get_volume(self):
        """Gets current volume percentage."""
        if not self.volume: return 0
        try:
            scalar = self.volume.GetMasterVolumeLevelScalar()
            return int(scalar * 100)
        except: return 0

    def adjust_volume(self, change: int):
        """Increases or decreases volume by a relative amount."""
        current = self.get_volume()
        new_level = current + change
        return self.set_volume(new_level)

    def mute_volume(self):
        """Toggles mute."""
        if not self.volume: return "Error: Audio interface not available."
        try:
            current_mute = self.volume.GetMute()
            self.volume.SetMute(not current_mute, None)
            state = "desactivado" if current_mute else "activado"
            return f"Silencio {state}."
        except Exception as e:
            return f"Error muteando: {e}"

    def set_brightness(self, level: int):
        """Sets screen brightness (0-100)."""
        try:
            level = max(0, min(100, level))
            sbc.set_brightness(level)
            return f"Brillo ajustado al {level}%."
        except Exception as e:
            logging.error(f"Error brightness: {e}")
            return "No pude ajustar el brillo (quizás no es un monitor compatible o laptop)."

    def media_play_pause(self):
        pyautogui.press('playpause')
        return "Media: Play/Pause"

    def media_next(self):
        pyautogui.press('nexttrack')
        return "Media: Siguiente"

    def media_prev(self):
        pyautogui.press('prevtrack')
        return "Media: Anterior"

    def lock_screen(self):
        import os
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Pantalla bloqueada"

    def turn_off_screen(self):
        """Turns off the monitor (using PowerShell/SendMessage)."""
        # This is a bit hacky but works on most Windows systems
        import ctypes
        try:
            SC_MONITORPOWER = 0xF170
            win32con_WM_SYSCOMMAND = 0x0112 
            mon_off = 2
            ctypes.windll.user32.SendMessageW(
                ctypes.windll.user32.GetForegroundWindow(),
                win32con_WM_SYSCOMMAND,
                SC_MONITORPOWER,
                mon_off
            )
            return "Apagando pantalla..."
        except Exception as e:
            return f"Error apagando pantalla: {e}"

    # ==========================================
    # NUEVAS FUNCIONES DE GESTIÓN (MÚSCULOS 💪)
    # ==========================================

    def kill_process(self, process_name: str):
        """Mata un proceso por su nombre."""
        import subprocess
        # Añadir .exe si falta y no es un nombre salvaje
        if not process_name.endswith(".exe"):
            process_name += ".exe"
            
        try:
            # /F = Force, /IM = Image Name
            result = subprocess.run(
                f"taskkill /F /IM {process_name}", 
                capture_output=True, text=True, shell=True
            )
            
            if "SUCCESS" in result.stdout or "ÉXITO" in result.stdout:
                return f"✅ Proceso {process_name} eliminado."
            elif "not found" in result.stderr or "no encontrado" in result.stderr:
                return f"⚠️ No encontré el proceso {process_name}."
            else:
                return f"❌ Error eliminando {process_name}: {result.stderr.strip()}"
        except Exception as e:
            return f"❌ Error ejecutando taskkill: {e}"

    def minimize_all_windows(self):
        """Minimiza todas las ventanas (Muestra Escritorio)."""
        # Win + D funciona como toggle
        pyautogui.hotkey('win', 'd')
        return "🖥️ Escritorio mostrado (Minimizar todo)."

    def maximize_window(self):
        """Maximiza la ventana actual."""
        pyautogui.hotkey('win', 'up')
        return "Ventana maximizada."

    def shutdown_system(self, minutes: int = 0):
        """Apaga el sistema tras N minutos."""
        import subprocess
        seconds = minutes * 60
        try:
            subprocess.run(f"shutdown /s /t {seconds}", shell=True)
            if minutes > 0:
                return f"🕒 Apagado programado en {minutes} minutos."
            return "👋 Apagando sistema ahora..."
        except Exception as e:
            return f"❌ Error al apagar: {e}"

    def restart_system(self, minutes: int = 0):
        """Reinicia el sistema tras N minutos."""
        import subprocess
        seconds = minutes * 60
        try:
            subprocess.run(f"shutdown /r /t {seconds}", shell=True)
            if minutes > 0:
                return f"🔄 Reinicio programado en {minutes} minutos."
            return "🔄 Reiniciando sistema ahora..."
        except Exception as e:
            return f"❌ Error al reiniciar: {e}"

    def cancel_shutdown(self):
        """Cancela cualquier apagado/reinicio programado."""
        import subprocess
        try:
            subprocess.run("shutdown /a", shell=True)
            return "✅ Apagado/Reinicio cancelado."
        except:
            return "ℹ️ No había apagado programado."

    def empty_recycle_bin(self):
        """Vacía la papelera de reciclaje (Requiere ctypes)."""
        import ctypes
        try:
            # SHEmptyRecycleBinW(hwnd, root_path, flags)
            # Flags: 1=NoConfirm, 2=NoProgress, 4=NoSound
            SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
            result = SHEmptyRecycleBin(None, None, 7) 
            if result == 0:
                return "🗑️ Papelera vaciada con éxito."
            elif result == -2147418113: # E_UNEXPECTED (A veces pasa si ya está vacía)
                 return "ℹ️ La papelera ya estaba vacía."
            else:
                return f"⚠️ Código de resultado: {result}"
        except Exception as e:
            return f"❌ Error vaciando papelera: {e}"

    def take_screenshot(self, folder_path="screenshots"):
        """Toma una captura de pantalla y la guarda con timestamp."""
        import os
        from datetime import datetime
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(folder_path, filename)
        
        try:
            pyautogui.screenshot(filepath)
            return f"📸 Captura guardada en: {filename}"
        except Exception as e:
            return f"❌ Error al tomar captura: {e}"

    def clean_temp_files(self):
        """Limpia archivos temporales del sistema (%TEMP%)."""
        import os
        import shutil
        
        temp_dir = os.environ.get('TEMP')
        if not temp_dir: return "❌ No encontré la carpeta TEMP."
        
        deleted_files = 0
        deleted_size = 0
        
        try:
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        size = os.path.getsize(fp)
                        os.remove(fp)
                        deleted_files += 1
                        deleted_size += size
                    except: pass # Archivo en uso
                    
            mb_freed = round(deleted_size / (1024*1024), 2)
            return f"🧹 Limpieza completada. {deleted_files} archivos borrados ({mb_freed} MB liberados)."
        except Exception as e:
            return f"❌ Error en limpieza: {e}"

    def get_heavy_processes(self, limit=5):
        """Devuelve los procesos que más RAM consumen."""
        try:
            import psutil
            # Obtener lista con detalles
            procs = []
            for p in psutil.process_iter(['name', 'memory_info']):
                try:
                    procs.append(p.info)
                except: pass
                
            # Ordenar por memoria (RSS)
            procs.sort(key=lambda p: p['memory_info'].rss, reverse=True)
            
            top = procs[:limit]
            reporte = "🚨 TOP PROCESOS (RAM):\n"
            for p in top:
                mem_mb = round(p['memory_info'].rss / (1024*1024), 1)
                reporte += f"• {p['name']}: {mem_mb} MB\n"
                
            return reporte
        except Exception as e:
            return f"❌ Error leyendo procesos: {e}"
    def close_window_by_title(self, partial_title: str):
        """Cierra ventanas que contengan partial_title en su título."""
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        WM_CLOSE = 0x0010
        
        found_count = 0
        
        def check_window(hwnd, _):
            nonlocal found_count
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                
                # Check visible windows only to avoid background processes
                if user32.IsWindowVisible(hwnd) and partial_title.lower() in title.lower():
                    # Enviar señal de cierre
                    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                    found_count += 1
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(check_window), 0)
        
        if found_count > 0:
            return f"✅ Cerrada(s) {found_count} ventana(s) con '{partial_title}'."
        else:
            return f"ℹ️ No encontré ventanas con '{partial_title}'."
    
    def deep_clean_system(self):
        """Limpieza profunda del sistema usando script BAT optimizado"""
        import subprocess
        import os
        
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "cleanup_system.bat")
        
        if not os.path.exists(script_path):
            return "❌ Script de limpieza no encontrado"
        
        try:
            # Ejecutar script BAT (mucho más rápido que Python)
            result = subprocess.run(script_path, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                return "✅ Limpieza profunda completada\n🗑️ Temporales, papelera y cache eliminados"
            else:
                return f"⚠️ Limpieza completada con advertencias"
        except Exception as e:
            return f"❌ Error en limpieza: {e}"

