"""
Pomodoro Manager - Sistema de productividad con técnica Pomodoro
Gestiona sesiones de trabajo (25 min) y descansos (5 min)
"""

import threading
import time
import json
import os
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict
import logging

class PomodoroManager:
    """Gestor de sesiones Pomodoro con estadísticas persistentes."""
    
    def __init__(self, voice_callback: Optional[Callable] = None):
        """
        Inicializa el gestor de Pomodoro.
        
        Args:
            voice_callback: Función para notificaciones de voz
        """
        self.voice_callback = voice_callback
        self.stats_file = "pomodoro_stats.json"
        
        # Configuración de tiempos (en segundos)
        self.work_duration = 25 * 60  # 25 minutos
        self.short_break_duration = 5 * 60  # 5 minutos
        self.long_break_duration = 15 * 60  # 15 minutos
        
        # Estado actual
        self.is_running = False
        self.is_paused = False
        self.current_session = None  # 'work', 'short_break', 'long_break'
        self.time_remaining = 0
        self.pomodoros_completed = 0
        self.session_start_time = None
        
        # Thread de timer
        self.timer_thread = None
        self.stop_flag = False
        
        # Cargar estadísticas
        self.stats = self._load_stats()
        
        logging.info("✅ PomodoroManager inicializado")
    
    def _load_stats(self) -> Dict:
        """Carga estadísticas desde archivo JSON."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error cargando stats de Pomodoro: {e}")
        
        # Estadísticas por defecto
        return {
            'total_pomodoros': 0,
            'total_work_time': 0,  # en minutos
            'total_break_time': 0,
            'sessions_by_date': {},
            'last_session': None
        }
    
    def _save_stats(self):
        """Guarda estadísticas en archivo JSON."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error guardando stats de Pomodoro: {e}")
    
    def start_work_session(self, duration_minutes: Optional[int] = None):
        """
        Inicia una sesión de trabajo.
        
        Args:
            duration_minutes: Duración personalizada en minutos (opcional)
        """
        if self.is_running:
            return "⚠️ Ya hay una sesión activa. Termínala primero."
        
        # Usar duración personalizada o por defecto
        if duration_minutes:
            self.work_duration = duration_minutes * 60
        
        self.current_session = 'work'
        self.time_remaining = self.work_duration
        self.is_running = True
        self.is_paused = False
        self.session_start_time = datetime.now()
        self.stop_flag = False
        
        # Iniciar thread de timer
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        # Notificación de voz
        if self.voice_callback:
            self.voice_callback("🍅 Pomodoro iniciado. 25 minutos de enfoque total.")
        
        logging.info(f"🍅 Sesión de trabajo iniciada: {self.work_duration // 60} minutos")
        return f"✅ Pomodoro iniciado: {self.work_duration // 60} minutos de trabajo"
    
    def start_break(self, long_break: bool = False):
        """
        Inicia un descanso.
        
        Args:
            long_break: Si es True, descanso largo (15 min), sino corto (5 min)
        """
        if self.is_running:
            return "⚠️ Ya hay una sesión activa."
        
        duration = self.long_break_duration if long_break else self.short_break_duration
        self.current_session = 'long_break' if long_break else 'short_break'
        self.time_remaining = duration
        self.is_running = True
        self.is_paused = False
        self.session_start_time = datetime.now()
        self.stop_flag = False
        
        # Iniciar thread de timer
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        # Notificación de voz
        break_type = "largo" if long_break else "corto"
        if self.voice_callback:
            self.voice_callback(f"☕ Descanso {break_type} iniciado. Relájate.")
        
        logging.info(f"☕ Descanso iniciado: {duration // 60} minutos")
        return f"✅ Descanso {break_type}: {duration // 60} minutos"
    
    def pause(self):
        """Pausa la sesión actual."""
        if not self.is_running:
            return "❌ No hay sesión activa para pausar."
        
        if self.is_paused:
            return "⚠️ La sesión ya está pausada."
        
        self.is_paused = True
        logging.info("⏸️ Pomodoro pausado")
        return "⏸️ Pomodoro pausado"
    
    def resume(self):
        """Reanuda la sesión pausada."""
        if not self.is_running:
            return "❌ No hay sesión activa para reanudar."
        
        if not self.is_paused:
            return "⚠️ La sesión no está pausada."
        
        self.is_paused = False
        logging.info("▶️ Pomodoro reanudado")
        return "▶️ Pomodoro reanudado"
    
    def stop(self):
        """Detiene la sesión actual."""
        if not self.is_running:
            return "❌ No hay sesión activa."
        
        self.stop_flag = True
        self.is_running = False
        self.is_paused = False
        
        # Guardar tiempo parcial si es sesión de trabajo
        if self.current_session == 'work':
            elapsed = self.work_duration - self.time_remaining
            self._record_partial_session(elapsed)
        
        logging.info("⏹️ Pomodoro detenido")
        return "⏹️ Pomodoro detenido"
    
    def _timer_loop(self):
        """Loop principal del timer (corre en thread separado)."""
        while self.time_remaining > 0 and not self.stop_flag:
            if not self.is_paused:
                time.sleep(1)
                self.time_remaining -= 1
            else:
                time.sleep(0.5)  # Check más frecuente cuando está pausado
        
        # Sesión completada
        if not self.stop_flag:
            self._on_session_complete()
    
    def _on_session_complete(self):
        """Callback cuando una sesión se completa."""
        session_type = self.current_session
        
        # Registrar estadísticas
        if session_type == 'work':
            self.pomodoros_completed += 1
            self._record_completed_pomodoro()
            
            # Notificación de voz
            if self.voice_callback:
                self.voice_callback(f"🎉 ¡Pomodoro completado! Llevas {self.pomodoros_completed} hoy. Toma un descanso.")
            
            # Auto-iniciar descanso si es cada 4 pomodoros
            if self.pomodoros_completed % 4 == 0:
                logging.info("🎯 4 pomodoros completados, descanso largo recomendado")
        
        elif session_type in ['short_break', 'long_break']:
            self._record_break_time()
            
            if self.voice_callback:
                self.voice_callback("✅ Descanso terminado. ¿Listo para otro pomodoro?")
        
        # Resetear estado
        self.is_running = False
        self.current_session = None
        self.time_remaining = 0
        
        logging.info(f"✅ Sesión {session_type} completada")
    
    def _record_completed_pomodoro(self):
        """Registra un pomodoro completado en las estadísticas."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.stats['total_pomodoros'] += 1
        self.stats['total_work_time'] += self.work_duration // 60
        self.stats['last_session'] = datetime.now().isoformat()
        
        # Estadísticas por fecha
        if today not in self.stats['sessions_by_date']:
            self.stats['sessions_by_date'][today] = {
                'pomodoros': 0,
                'work_minutes': 0,
                'break_minutes': 0
            }
        
        self.stats['sessions_by_date'][today]['pomodoros'] += 1
        self.stats['sessions_by_date'][today]['work_minutes'] += self.work_duration // 60
        
        self._save_stats()
    
    def _record_break_time(self):
        """Registra tiempo de descanso."""
        today = datetime.now().strftime('%Y-%m-%d')
        duration = self.long_break_duration if self.current_session == 'long_break' else self.short_break_duration
        
        self.stats['total_break_time'] += duration // 60
        
        if today in self.stats['sessions_by_date']:
            self.stats['sessions_by_date'][today]['break_minutes'] += duration // 60
        
        self._save_stats()
    
    def _record_partial_session(self, elapsed_seconds: int):
        """Registra una sesión parcial (detenida antes de completar)."""
        today = datetime.now().strftime('%Y-%m-%d')
        minutes = elapsed_seconds // 60
        
        if minutes > 0:
            self.stats['total_work_time'] += minutes
            
            if today in self.stats['sessions_by_date']:
                self.stats['sessions_by_date'][today]['work_minutes'] += minutes
            
            self._save_stats()
    
    def get_status(self) -> Dict:
        """
        Obtiene el estado actual del Pomodoro.
        
        Returns:
            Diccionario con estado actual
        """
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'session_type': self.current_session,
            'time_remaining': self.time_remaining,
            'time_remaining_formatted': self._format_time(self.time_remaining),
            'pomodoros_today': self.pomodoros_completed,
            'total_pomodoros': self.stats['total_pomodoros']
        }
    
    def get_statistics(self) -> str:
        """
        Genera un reporte de estadísticas.
        
        Returns:
            String formateado con estadísticas
        """
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = self.stats['sessions_by_date'].get(today, {
            'pomodoros': 0,
            'work_minutes': 0,
            'break_minutes': 0
        })
        
        report = "📊 ESTADÍSTICAS DE POMODORO\n"
        report += "=" * 30 + "\n\n"
        
        report += "📅 HOY:\n"
        report += f"  🍅 Pomodoros: {today_stats['pomodoros']}\n"
        report += f"  ⏱️ Trabajo: {today_stats['work_minutes']} min\n"
        report += f"  ☕ Descanso: {today_stats['break_minutes']} min\n\n"
        
        report += "📈 TOTAL:\n"
        report += f"  🍅 Pomodoros: {self.stats['total_pomodoros']}\n"
        report += f"  ⏱️ Trabajo: {self.stats['total_work_time']} min ({self.stats['total_work_time'] // 60}h {self.stats['total_work_time'] % 60}m)\n"
        report += f"  ☕ Descanso: {self.stats['total_break_time']} min\n\n"
        
        # Última sesión
        if self.stats['last_session']:
            last = datetime.fromisoformat(self.stats['last_session'])
            report += f"🕐 Última sesión: {last.strftime('%d/%m/%Y %H:%M')}\n"
        
        return report
    
    def configure(self, work_minutes: int = 25, short_break: int = 5, long_break: int = 15):
        """
        Configura duraciones personalizadas.
        
        Args:
            work_minutes: Duración de trabajo en minutos
            short_break: Duración de descanso corto en minutos
            long_break: Duración de descanso largo en minutos
        """
        if self.is_running:
            return "⚠️ No puedes cambiar la configuración con una sesión activa."
        
        self.work_duration = work_minutes * 60
        self.short_break_duration = short_break * 60
        self.long_break_duration = long_break * 60
        
        logging.info(f"⚙️ Pomodoro configurado: {work_minutes}/{short_break}/{long_break} min")
        return f"✅ Configuración actualizada: {work_minutes}/{short_break}/{long_break} min"
    
    @staticmethod
    def _format_time(seconds: int) -> str:
        """Formatea segundos a MM:SS."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def reset_daily_counter(self):
        """Resetea el contador de pomodoros del día."""
        self.pomodoros_completed = 0
        logging.info("🔄 Contador diario reseteado")
        return "🔄 Contador de hoy reseteado"


# Singleton para acceso global
_pomodoro_instance = None

def obtener_pomodoro(voice_callback: Optional[Callable] = None) -> PomodoroManager:
    """
    Obtiene la instancia singleton de PomodoroManager.
    
    Args:
        voice_callback: Función para notificaciones de voz
    
    Returns:
        Instancia de PomodoroManager
    """
    global _pomodoro_instance
    if _pomodoro_instance is None:
        _pomodoro_instance = PomodoroManager(voice_callback)
    return _pomodoro_instance
