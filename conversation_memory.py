"""
SARA - Conversation Memory
Sistema de memoria contextual para conversaciones naturales
"""
from datetime import datetime
from typing import List, Dict, Optional
import logging

class ConversationMemory:
    """Gestiona el contexto de conversaciones para respuestas más inteligentes"""
    
    def __init__(self, max_history: int = 10):
        """
        Inicializa la memoria de conversación
        
        Args:
            max_history: Número máximo de turnos a recordar
        """
        self.history: List[Dict] = []
        self.context: Dict = {}
        self.max_history = max_history
        self.current_topic = None
        
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
            "timestamp": datetime.now(),
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
        Detecta el tema de la conversación
        
        Args:
            text: Texto del usuario
            
        Returns:
            Tema detectado o None
        """
        text_lower = text.lower()
        
        # Temas comunes
        topics = {
            "clima": ["clima", "tiempo", "temperatura", "lluvia", "sol"],
            "calendario": ["calendario", "eventos", "reunión", "cita"],
            "música": ["música", "canción", "reproduce", "spotify"],
            "red": ["red", "dispositivos", "wifi", "internet"],
            "trabajo": ["trabajo", "productividad", "pomodoro"],
            "noticias": ["noticias", "actualidad", "noticia"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return None
    
    def get_last_topic(self) -> Optional[str]:
        """Obtiene el último tema de conversación"""
        return self.current_topic
    
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
            "mañana", "ayer", "después", "antes"
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
        logging.info("Memoria de conversación limpiada")
    
    def get_summary(self) -> str:
        """Obtiene un resumen de la memoria actual"""
        if not self.history:
            return "No hay conversación en memoria"
        
        return f"Memoria: {len(self.history)} turnos | Tema: {self.current_topic or 'ninguno'}"
