import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

class HealthMonitor:
    """Monitor de salud que rastrea sesiones de trabajo y envía recordatorios de bienestar"""
    
    def __init__(self):
        self.is_active = False
        self.is_paused = False
        self.start_time: Optional[datetime] = None
        self.pause_time: Optional[datetime] = None
        self.total_paused_seconds = 0
        self.current_profile = "casa"  # casa, oficina, pomodoro
        self.last_reminders: Dict[str, datetime] = {}
        self.session_history: List[Dict] = []
        
        # Perfiles de recordatorios (minutos)
        self.profiles = {
            "casa": [
                (20, "👁️ Ojos", "Regla 20-20-20: Mira algo a 6 metros por 20 segundos", 0.5),
                (30, "🧘 Micro", "Estira cuello y hombros. Respira profundo", 2),
                (45, "💧 Hidratación", "Toma agua. Aprovecha para caminar", 2),
                (60, "🚶 Movimiento", "1 hora completa. Levántate, camina, estira piernas", 5),
                (90, "🧠 Mental", "Descanso mental. Sal de la pantalla 10 minutos", 10),
                (120, "☕ Largo", "2 horas trabajadas. Descanso real de 15 minutos", 15)
            ],
            "oficina": [
                (20, "👁️ Ojos", "Descansa la vista 20 segundos", 0.3),
                (50, "🤏 Micro", "Estira manos y muñecas discretamente", 1),
                (60, "💧 Hidratación", "Ve por agua o al baño", 3),
                (120, "☕ Break", "2 horas. Toma tu break oficial", 10)
            ],
            "pomodoro": [
                (25, "🍅 Pomodoro", "25 minutos completados. Descansa 5 minutos", 5)
            ]
        }
        
        self.pomodoro_count = 0
    
    def start_session(self, profile: str = "casa") -> str:
        """Inicia una sesión de trabajo"""
        if self.is_active and not self.is_paused:
            return "⚠️ Ya hay una sesión activa. Di 'pausa trabajo' primero."
        
        if profile not in self.profiles:
            return f"❌ Perfil '{profile}' no existe. Usa: casa, oficina o pomodoro"
        
        self.current_profile = profile
        self.is_active = True
        self.is_paused = False
        self.start_time = datetime.now()
        self.total_paused_seconds = 0
        self.last_reminders = {}
        self.pomodoro_count = 0
        
        profile_names = {
            "casa": "🏠 Casa (Flexible)",
            "oficina": "🏢 Oficina (Discreto)",
            "pomodoro": "🍅 Pomodoro (Concentración)"
        }
        
        return f"✅ Sesión iniciada en modo {profile_names[profile]}. ¡A trabajar con salud!"
    
    def pause_session(self) -> str:
        """Pausa la sesión actual"""
        if not self.is_active:
            return "❌ No hay sesión activa."
        
        if self.is_paused:
            return "⚠️ La sesión ya está pausada."
        
        self.is_paused = True
        self.pause_time = datetime.now()
        return "⏸️ Sesión pausada. Di 'reanudar trabajo' cuando vuelvas."
    
    def resume_session(self) -> str:
        """Reanuda la sesión pausada"""
        if not self.is_active:
            return "❌ No hay sesión activa."
        
        if not self.is_paused:
            return "⚠️ La sesión no está pausada."
        
        # Calcular tiempo pausado
        if self.pause_time:
            paused_duration = (datetime.now() - self.pause_time).total_seconds()
            self.total_paused_seconds += paused_duration
        
        self.is_paused = False
        self.pause_time = None
        return "▶️ Sesión reanudada. ¡Sigamos!"
    
    def stop_session(self) -> str:
        """Finaliza la sesión y devuelve resumen"""
        if not self.is_active:
            return "❌ No hay sesión activa."
        
        # Calcular tiempo total
        if self.is_paused and self.pause_time:
            paused_duration = (datetime.now() - self.pause_time).total_seconds()
            self.total_paused_seconds += paused_duration
        
        total_seconds = (datetime.now() - self.start_time).total_seconds() - self.total_paused_seconds
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        # Guardar en historial
        self.session_history.append({
            "start": self.start_time,
            "end": datetime.now(),
            "duration_minutes": int(total_seconds / 60),
            "profile": self.current_profile
        })
        
        # Reset
        self.is_active = False
        self.is_paused = False
        
        summary = f"🏁 Sesión finalizada\n"
        summary += f"⏱️ Tiempo trabajado: {hours}h {minutes}min\n"
        summary += f"📊 Perfil: {self.current_profile.capitalize()}\n"
        
        if self.current_profile == "pomodoro":
            summary += f"🍅 Pomodoros completados: {self.pomodoro_count}\n"
        
        summary += "\n¡Buen trabajo! Recuerda descansar."
        
        return summary
    
    def get_elapsed_time(self) -> str:
        """Obtiene el tiempo transcurrido en la sesión actual"""
        if not self.is_active:
            return "❌ No hay sesión activa."
        
        if self.is_paused:
            total_seconds = (self.pause_time - self.start_time).total_seconds() - self.total_paused_seconds
        else:
            total_seconds = (datetime.now() - self.start_time).total_seconds() - self.total_paused_seconds
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        status = "⏸️ (Pausado)" if self.is_paused else "▶️"
        return f"{status} Llevas {hours}h {minutes}min trabajando"
    
    def check_reminders(self) -> Optional[Tuple[str, str, str]]:
        """Verifica si hay recordatorios pendientes. Retorna (emoji, tipo, mensaje) o None"""
        if not self.is_active or self.is_paused:
            return None
        
        elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60 - (self.total_paused_seconds / 60)
        
        for interval, emoji, message, duration in self.profiles[self.current_profile]:
            reminder_key = f"{interval}_{emoji}"
            
            # Verificar si ya pasó el intervalo y no se ha enviado este recordatorio
            if elapsed_minutes >= interval:
                # Para recordatorios repetitivos, verificar si han pasado suficientes minutos desde el último
                if reminder_key in self.last_reminders:
                    last_time = self.last_reminders[reminder_key]
                    minutes_since_last = (datetime.now() - last_time).total_seconds() / 60
                    
                    # Solo enviar si han pasado al menos 'interval' minutos desde el último
                    if minutes_since_last < interval:
                        continue
                
                # Marcar como enviado
                self.last_reminders[reminder_key] = datetime.now()
                
                # Incrementar contador de pomodoro
                if self.current_profile == "pomodoro":
                    self.pomodoro_count += 1
                    if self.pomodoro_count % 4 == 0:
                        message = "🍅 4 Pomodoros completados! Descanso largo de 15-30 minutos"
                
                return (emoji, f"{emoji} {interval}min", message)
        
        return None
    
    def get_next_reminder(self) -> str:
        """Obtiene información del próximo recordatorio"""
        if not self.is_active:
            return "❌ No hay sesión activa."
        
        elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60 - (self.total_paused_seconds / 60)
        
        # Buscar el próximo recordatorio
        next_reminder = None
        min_diff = float('inf')
        
        for interval, emoji, message, duration in self.profiles[self.current_profile]:
            diff = interval - elapsed_minutes
            if diff > 0 and diff < min_diff:
                min_diff = diff
                next_reminder = (interval, emoji, message)
        
        if next_reminder:
            interval, emoji, message = next_reminder
            minutes_left = int(min_diff)
            return f"⏰ Próximo: {emoji} en {minutes_left} minutos\n💡 {message}"
        else:
            return "✅ Has completado todos los intervalos del ciclo actual"
    
    def change_profile(self, new_profile: str) -> str:
        """Cambia el perfil de la sesión actual"""
        if not self.is_active:
            return "❌ No hay sesión activa. Inicia una con 'voy a trabajar'"
        
        if new_profile not in self.profiles:
            return f"❌ Perfil '{new_profile}' no existe. Usa: casa, oficina o pomodoro"
        
        old_profile = self.current_profile
        self.current_profile = new_profile
        self.last_reminders = {}  # Reset recordatorios
        
        return f"✅ Perfil cambiado de {old_profile} → {new_profile}"
