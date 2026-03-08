"""
🧪 SARA - Test Suite for Health Monitor
========================================

Tests para el módulo de monitor de salud.
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from health_monitor import HealthMonitor


class TestHealthMonitorInitialization:
    """Tests para inicialización del monitor"""
    
    def test_create_monitor(self):
        """Test: Crear monitor de salud"""
        monitor = HealthMonitor()
        assert monitor is not None
        assert monitor.is_active == False
        assert monitor.is_paused == False
    
    def test_initial_state(self):
        """Test: Estado inicial del monitor"""
        monitor = HealthMonitor()
        assert monitor.start_time is None
        assert monitor.current_profile == "casa"  # Tiene valor por defecto


class TestSessionManagement:
    """Tests para manejo de sesiones"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_start_session_casa(self, monitor):
        """Test: Iniciar sesión de casa"""
        result = monitor.start_session("casa")
        
        assert monitor.is_active == True
        assert monitor.current_profile == "casa"
        assert monitor.start_time is not None
        assert isinstance(result, str)
    
    def test_start_session_oficina(self, monitor):
        """Test: Iniciar sesión de oficina"""
        result = monitor.start_session("oficina")
        
        assert monitor.is_active == True
        assert monitor.current_profile == "oficina"
    
    def test_start_session_pomodoro(self, monitor):
        """Test: Iniciar sesión pomodoro"""
        result = monitor.start_session("pomodoro")
        
        assert monitor.is_active == True
        assert monitor.current_profile == "pomodoro"
    
    def test_start_session_invalid_profile(self, monitor):
        """Test: Iniciar sesión con perfil inválido"""
        result = monitor.start_session("perfil_invalido")
        
        # Debería usar perfil por defecto o rechazar
        assert isinstance(result, str)
    
    def test_stop_session(self, monitor):
        """Test: Detener sesión"""
        monitor.start_session("casa")
        time.sleep(0.1)  # Esperar un poco
        
        summary = monitor.stop_session()
        
        assert monitor.is_active == False
        assert isinstance(summary, str)  # Retorna string, no dict
        assert "tiempo" in summary.lower() or "sesión" in summary.lower()


class TestSessionPauseResume:
    """Tests para pausar/reanudar sesiones"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_pause_session(self, monitor):
        """Test: Pausar sesión"""
        monitor.start_session("casa")
        result = monitor.pause_session()
        
        assert monitor.is_paused == True
        assert isinstance(result, str)
    
    def test_pause_without_session(self, monitor):
        """Test: Pausar sin sesión activa"""
        result = monitor.pause_session()
        # No debería crashear
        assert isinstance(result, str)
    
    def test_resume_session(self, monitor):
        """Test: Reanudar sesión"""
        monitor.start_session("casa")
        monitor.pause_session()
        
        result = monitor.resume_session()
        
        assert monitor.is_paused == False
        assert isinstance(result, str)
    
    def test_resume_without_pause(self, monitor):
        """Test: Reanudar sin estar pausado"""
        monitor.start_session("casa")
        result = monitor.resume_session()
        # No debería crashear
        assert isinstance(result, str)


class TestElapsedTime:
    """Tests para tiempo transcurrido"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_get_elapsed_time_active(self, monitor):
        """Test: Obtener tiempo transcurrido en sesión activa"""
        monitor.start_session("casa")
        time.sleep(0.2)  # Esperar 200ms
        
        elapsed = monitor.get_elapsed_time()
        
        assert isinstance(elapsed, str)
        # Debería contener información de tiempo (usa "min" no "minuto")
        assert any(word in elapsed.lower() for word in ["min", "hora", "llevas"])
    
    def test_get_elapsed_time_inactive(self, monitor):
        """Test: Obtener tiempo sin sesión activa"""
        elapsed = monitor.get_elapsed_time()
        assert isinstance(elapsed, str)


class TestReminders:
    """Tests para recordatorios"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_check_reminders_no_session(self, monitor):
        """Test: Verificar recordatorios sin sesión"""
        reminder = monitor.check_reminders()
        assert reminder is None
    
    def test_check_reminders_active_session(self, monitor):
        """Test: Verificar recordatorios con sesión activa"""
        monitor.start_session("casa")
        reminder = monitor.check_reminders()
        
        # Puede ser None si no hay recordatorios pendientes
        assert reminder is None or isinstance(reminder, tuple)
    
    def test_get_next_reminder(self, monitor):
        """Test: Obtener próximo recordatorio"""
        monitor.start_session("casa")
        next_reminder = monitor.get_next_reminder()
        
        assert isinstance(next_reminder, str)


class TestProfileChange:
    """Tests para cambio de perfil"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_change_profile_during_session(self, monitor):
        """Test: Cambiar perfil durante sesión"""
        monitor.start_session("casa")
        result = monitor.change_profile("oficina")
        
        assert monitor.current_profile == "oficina"
        assert isinstance(result, str)
    
    def test_change_profile_without_session(self, monitor):
        """Test: Cambiar perfil sin sesión activa"""
        result = monitor.change_profile("oficina")
        # No debería crashear
        assert isinstance(result, str)


class TestWorkProfiles:
    """Tests para perfiles de trabajo específicos"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_casa_profile_settings(self, monitor):
        """Test: Configuración de perfil casa"""
        monitor.start_session("casa")
        # Perfil casa: 50min trabajo / 10min descanso
        assert monitor.current_profile == "casa"
    
    def test_oficina_profile_settings(self, monitor):
        """Test: Configuración de perfil oficina"""
        monitor.start_session("oficina")
        # Perfil oficina: 90min trabajo / 15min descanso
        assert monitor.current_profile == "oficina"
    
    def test_pomodoro_profile_settings(self, monitor):
        """Test: Configuración de perfil pomodoro"""
        monitor.start_session("pomodoro")
        # Perfil pomodoro: 25min trabajo / 5min descanso
        assert monitor.current_profile == "pomodoro"


class TestSessionStatistics:
    """Tests para estadísticas de sesión"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_session_summary_structure(self, monitor):
        """Test: Estructura del resumen de sesión"""
        monitor.start_session("casa")
        time.sleep(0.1)
        summary = monitor.stop_session()
        
        assert isinstance(summary, str)  # Retorna string, no dict
        # Verificar que tiene información relevante
        assert len(summary) > 0
        assert "sesión" in summary.lower() or "trabajo" in summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
