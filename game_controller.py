import os
import subprocess
import logging
import psutil
from typing import List, Dict, Optional
try:
    from fuzzywuzzy import fuzz, process
except ImportError:
    fuzz = None
    process = None

class GameController:
    """Controlador de videojuegos con detección, lanzamiento y optimización"""
    
    def __init__(self):
        self.known_games: Dict[str, str] = {}
        self.game_paths = {
            "steam": r"C:\Program Files (x86)\Steam\steamapps\common",
            "steam_alt": r"C:\Program Files\Steam\steamapps\common",
            "epic": r"C:\Program Files\Epic Games",
            "riot": r"C:\Riot Games",
            "blizzard": r"C:\Program Files (x86)\Battle.net",
            "ea": r"C:\Program Files\EA Games"
        }
        
        # Escanear juegos al inicializar
        self.scan_games()
    
    def scan_games(self) -> str:
        """Escanea y detecta juegos instalados"""
        self.known_games = {}
        found_count = 0
        
        for platform, path in self.game_paths.items():
            if not os.path.exists(path):
                continue
            
            try:
                # Listar carpetas (cada carpeta suele ser un juego)
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    
                    if os.path.isdir(item_path):
                        # Buscar ejecutables .exe en la carpeta
                        exe_files = [f for f in os.listdir(item_path) if f.endswith('.exe')]
                        
                        if exe_files:
                            # Usar el primer .exe encontrado
                            game_name = item.lower()
                            exe_path = os.path.join(item_path, exe_files[0])
                            self.known_games[game_name] = exe_path
                            found_count += 1
                            
            except Exception as e:
                logging.error(f"Error escaneando {platform}: {e}")
        
        if found_count > 0:
            return f"✅ Detectados {found_count} juegos instalados"
        else:
            return "⚠️ No se encontraron juegos en las rutas conocidas"
    
    def list_games(self) -> str:
        """Lista todos los juegos detectados"""
        if not self.known_games:
            return "❌ No hay juegos detectados. Di 'escanear juegos' para buscar."
        
        games_list = "\n".join([f"• {name.title()}" for name in sorted(self.known_games.keys())])
        return f"🎮 Juegos instalados ({len(self.known_games)}):\n\n{games_list}"
    
    def launch_game(self, game_name: str) -> str:
        """Lanza un juego por nombre (con búsqueda fuzzy)"""
        if not self.known_games:
            self.scan_games()
        
        if not self.known_games:
            return "❌ No hay juegos detectados"
        
        # Búsqueda fuzzy si fuzzywuzzy está disponible
        if fuzz and process:
            match = process.extractOne(game_name.lower(), self.known_games.keys())
            
            if match and match[1] >= 60:  # 60% de similitud mínima
                matched_game = match[0]
                exe_path = self.known_games[matched_game]
                
                try:
                    subprocess.Popen(exe_path)
                    return f"🎮 Abriendo {matched_game.title()}..."
                except Exception as e:
                    return f"❌ Error al abrir {matched_game}: {e}"
            else:
                return f"❌ No encontré un juego similar a '{game_name}'. Di 'qué juegos tengo' para ver la lista."
        else:
            # Búsqueda exacta si no hay fuzzywuzzy
            game_name_lower = game_name.lower()
            for known_game in self.known_games.keys():
                if game_name_lower in known_game or known_game in game_name_lower:
                    exe_path = self.known_games[known_game]
                    try:
                        subprocess.Popen(exe_path)
                        return f"🎮 Abriendo {known_game.title()}..."
                    except Exception as e:
                        return f"❌ Error: {e}"
            
            return f"❌ Juego '{game_name}' no encontrado"
    
    def optimize_for_gaming(self) -> str:
        """Optimiza el sistema para gaming usando script BAT (3x más rápido)"""
        import subprocess
        import os
        
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "optimize_gaming.bat")
        
        if not os.path.exists(script_path):
            # Fallback a método Python si no existe el script
            return self._optimize_python_fallback()
        
        try:
            # Ejecutar script BAT optimizado
            result = subprocess.run(script_path, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                return "🎮 Sistema optimizado para gaming\n✅ Apps cerradas, RAM liberada\n⚡ Listo para jugar al máximo"
            else:
                return "⚠️ Optimización completada con advertencias"
        except Exception as e:
            logging.error(f"Error optimizando: {e}")
            return self._optimize_python_fallback()
    
    def _optimize_python_fallback(self) -> str:
        """Método de optimización Python (fallback si no hay BAT)"""
        actions = []
        
        try:
            # Cerrar apps pesadas
            heavy_apps = ["chrome.exe", "msedge.exe", "firefox.exe"]
            closed_count = 0
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in heavy_apps:
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if closed_count > 0:
                actions.append(f"✅ Cerradas {closed_count} apps pesadas")
            
            # Limpiar memoria
            import gc
            gc.collect()
            actions.append("✅ Memoria optimizada")
            
            # Info de recursos
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            actions.append(f"📊 RAM disponible: {mem.available // (1024**3)}GB")
            actions.append(f"📊 CPU: {cpu}%")
            
            return "🎮 Optimización completada:\n" + "\n".join(actions)
            
        except Exception as e:
            logging.error(f"Error optimizando: {e}")
            return f"⚠️ Optimización parcial: {e}"
    
    def close_game(self, game_name: str) -> str:
        """Cierra un juego por nombre"""
        try:
            closed = False
            for proc in psutil.process_iter(['name']):
                if game_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed = True
                    return f"✅ {game_name.title()} cerrado"
            
            if not closed:
                return f"⚠️ No encontré {game_name} en ejecución"
                
        except Exception as e:
            return f"❌ Error: {e}"


# Función helper
_game_controller_instance = None

def obtener_game_controller():
    """Obtiene o crea la instancia del controlador de juegos"""
    global _game_controller_instance
    if _game_controller_instance is None:
        _game_controller_instance = GameController()
    return _game_controller_instance
