"""
SARA - Rutinas y Automatización
Sistema para ejecutar secuencias de comandos predefinidas o programadas
"""
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any

class RoutineManager:
    """Gestiona rutinas y automatizaciones"""
    
    def __init__(self, brain_ref):
        """
        Inicializa el gestor de rutinas
        
        Args:
            brain_ref: Referencia al cerebro de SARA para ejecutar comandos
        """
        self.brain = brain_ref
        self.routines: Dict[str, Dict] = {}
        self._load_default_routines()
        
    def _load_default_routines(self):
        """Carga rutinas por defecto"""
        self.routines = {
            "buenos_dias": {
                "name": "Buenos Días",
                "description": "Rutina matutina para empezar el día",
                "actions": [
                    {"type": "speak", "text": "¡Buenos días {user_name}! Espero que hayas descansado bien."},
                    {"type": "command", "cmd": "hora"},
                    {"type": "command", "cmd": "clima"},
                    {"type": "command", "cmd": "leer calendario hoy"}, # Futura integración
                    {"type": "speak", "text": "¡A por todas hoy!"}
                ]
            },
            "modo_trabajo": {
                "name": "Modo Trabajo",
                "description": "Prepara el entorno para trabajar",
                "actions": [
                    {"type": "speak", "text": "Activando modo trabajo. Concentración al máximo."},
                    {"type": "command", "cmd": "silencio"}, # Mute audio
                    {"type": "command", "cmd": "pomodoro iniciar"},
                    {"type": "command", "cmd": "vigilancia red"}, # Network Guardian
                    {"type": "speak", "text": "Sistema listo para trabajar."}
                ]
            },
            "fin_trabajo": {
                "name": "Fin de Trabajo",
                "description": "Cierra el día laboral",
                "actions": [
                    {"type": "speak", "text": "¡Excelente trabajo hoy! Es hora de descansar."},
                    {"type": "command", "cmd": "pomodoro detener"},
                    {"type": "command", "cmd": "volumen 50"}, # Restaurar volumen
                    {"type": "command", "cmd": "resumen dia"}, # Futuro
                    {"type": "speak", "text": "Hasta mañana."}
                ]
            }
        }
        logging.info(f"✅ Rutinas cargadas: {len(self.routines)}")
    
    def execute_routine(self, routine_key: str) -> str:
        """
        Ejecuta una rutina específica
        
        Args:
            routine_key: Clave de la rutina (ej: 'buenos_dias')
            
        Returns:
            Mensaje de resultado
        """
        routine_key = routine_key.lower().replace(" ", "_")
        
        # Buscar clave similar si no es exacta
        if routine_key not in self.routines:
            for key in self.routines:
                if routine_key in key or key in routine_key:
                    routine_key = key
                    break
        
        if routine_key not in self.routines:
            return f"No encontré la rutina '{routine_key}'"
            
        routine = self.routines[routine_key]
        logging.info(f"Ejecutando rutina: {routine['name']}")
        
        # Ejecutar en un hilo separado para no bloquear
        threading.Thread(target=self._execute_actions, args=(routine,)).start()
        
        return f"Ejecutando rutina {routine['name']}..."
    
    def _execute_actions(self, routine: Dict):
        """Ejecuta las acciones de una rutina secuencialmente"""
        user_name = "Usuario"
        if hasattr(self.brain, 'perfil') and self.brain.perfil:
            user_name = self.brain.perfil.profile["user"]["preferred_name"] or "Usuario"
            
        for action in routine["actions"]:
            try:
                if action["type"] == "speak":
                    text = action["text"].format(user_name=user_name)
                    self.brain.voz.hablar(text)
                    # Esperar un poco (estimado)
                    time.sleep(len(text) * 0.08 + 1)
                    
                elif action["type"] == "command":
                    cmd = action["cmd"]
                    logging.info(f"Rutina acción: {cmd}")
                    self.brain.procesar(cmd)
                    time.sleep(1) # Pausa entre comandos
                    
                elif action["type"] == "wait":
                    time.sleep(action.get("seconds", 1))
                    
            except Exception as e:
                logging.error(f"Error en acción de rutina: {e}")
        
        logging.info(f"Rutina {routine['name']} finalizada")

    def get_available_routines(self) -> str:
        """Devuelve lista de rutinas disponibles"""
        names = [r["name"] for r in self.routines.values()]
        return "Rutinas disponibles: " + ", ".join(names)

def obtener_rutinas(brain_ref):
    return RoutineManager(brain_ref)
