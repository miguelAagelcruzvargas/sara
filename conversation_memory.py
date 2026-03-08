"""
SARA - Conversation Memory
Sistema de memoria contextual para conversaciones naturales
"""
from datetime import datetime
from typing import List, Dict, Optional
import logging
import json
import os

MEMORY_FILE = "conversation_history.json"

class ConversationMemory:
    """Gestiona el contexto de conversaciones para respuestas más inteligentes"""
    
    def __init__(self, max_history: int = 15): # Aumentado de 10 a 15
        """
        Inicializa la memoria de conversación
        
        Args:
            max_history: Número máximo de turnos a recordar
        """
        self.history: List[Dict] = []
        self.context: Dict = {}
        self.max_history = max_history
        self.current_topic = None
        
        # Cargar memoria persistente al iniciar
        self.load_memory()
        
    def add_turn(self, user_input: str, sara_response: str, intent: Optional[str] = None):
        """
        Agrega un turno de conversación a la memoria
        
        Args:
            user_input: Lo que dijo el usuario
            sara_response: Respuesta de SARA
            intent: Intención detectada (opcional)
        """
        turn = {
            "user": user_input,
            "sara": sara_response,
            "intent": intent,
            "timestamp": datetime.now().isoformat(), # Serializar fecha para JSON
            "topic": self._detect_topic(user_input)
        }
        
        self.history.append(turn)
        
        # Actualizar topic actual
        if turn["topic"]:
            self.current_topic = turn["topic"]
        
        # Mantener solo últimos N turnos
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        logging.debug(f"Memoria: Agregado turno. Total: {len(self.history)}")
        
        # Guardar cambios
        self.save_memory()
    
    def save_memory(self):
        """Guarda la memoria en disco (Persistencia)"""
        try:
            data = {
                "history": self.history,
                "current_topic": self.current_topic,
                "context": self.context,
                "last_modified": datetime.now().isoformat()
            }
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error guardando memoria: {e}")

    def load_memory(self):
        """Carga la memoria desde disco"""
        if not os.path.exists(MEMORY_FILE):
            return
            
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.current_topic = data.get("current_topic")
                self.context = data.get("context", {})
                
                # Truncar si es necesario (por si se cambió max_history)
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                    
            logging.info(f"Memoria cargada: {len(self.history)} turnos previos. Tema: {self.current_topic}")
        except Exception as e:
            logging.error(f"Error cargando memoria (se iniciará vacía): {e}")

    def get_context_prompt(self, include_last_n: int = 3) -> str:
        """
        Genera un prompt con el contexto de conversación reciente
        
        Args:
            include_last_n: Número de turnos recientes a incluir
            
        Returns:
            String con el contexto formateado
        """
        if not self.history:
            return ""
        
        # Tomar últimos N turnos
        recent_turns = self.history[-include_last_n:]
        
        context = "Contexto de conversación reciente:\n"
        for turn in recent_turns:
            context += f"Usuario: {turn['user']}\n"
            context += f"SARA: {turn['sara']}\n"
        
        if self.current_topic:
            context += f"\nTema actual: {self.current_topic}\n"
        
        return context
    
    def _detect_topic(self, text: str) -> Optional[str]:
        """
        Detecta el tema de la conversación usando palabras clave flexibles
        
        Args:
            text: Texto del usuario
            
        Returns:
            Tema detectado o None
        """
        text_lower = text.lower()
        
        # Temas ampliados y flexibles (con raíces/stems simples)
        topics = {
            "clima": ["clima", "tiempo", "temperatura", "lluvia", "sol", "frio", "calor", "nublad", "pronostic"],
            "calendario": ["calendario", "evento", "reunión", "cita", "agenda", "recordatori"],
            "música": ["música", "cancion", "reproduc", "spotify", "youtube", "toca", "pon ", "escuchar", "rola", "temazo", "disco", "artista"],
            "red": ["red", "dispositiv", "wifi", "internet", "conec", "lag", "ping", "velocidad"],
            "trabajo": ["trabajo", "productiv", "pomodoro", "concentra", "estudio", "tarea", "laboral"],
            "noticias": ["noticia", "actualidad", "sucedie", "pasando", "mundo"],
            "sistema": ["volumen", "brillo", "bateria", "pantalla", "minimiza", "cierra", "apaga", "reinicia", "pc"],
            "identidad": ["quien eres", "nombre", "creador", "version", "eres", "hola"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return None
    
    def get_last_topic(self) -> Optional[str]:
        """Obtiene el último tema de conversación"""
        return self.current_topic

    def get_last_turn(self) -> Optional[Dict]:
        """Obtiene el último turno de la memoria"""
        if not self.history:
            return None
        return self.history[-1]
    
    def is_follow_up_question(self, text: str) -> bool:
        """
        Detecta si es una pregunta de seguimiento
        
        Args:
            text: Texto del usuario
            
        Returns:
            True si parece ser una pregunta de seguimiento
        """
        follow_up_indicators = [
            "y ", "¿y ", "también", "además", "otro", "otra",
            "qué más", "cuál", "cuándo", "dónde", "cómo",
            "mañana", "ayer", "después", "antes", "entonces"
        ]
        
        text_lower = text.lower().strip()
        
        # Si es muy corta y tiene indicadores, probablemente es seguimiento
        if len(text_lower.split()) <= 5:
            return any(text_lower.startswith(ind) for ind in follow_up_indicators)
        
        return False
    
    def clear(self):
        """Limpia toda la memoria de conversación"""
        self.history.clear()
        self.context.clear()
        self.current_topic = None
        
        # Guardar estado vacío
        self.save_memory()
        logging.info("Memoria de conversación limpiada")
    
    def get_summary(self) -> str:
        """Obtiene un resumen de la memoria actual"""
        if not self.history:
            return "No hay conversación en memoria"
        
        return f"Memoria: {len(self.history)} turnos | Tema: {self.current_topic or 'ninguno'}"
