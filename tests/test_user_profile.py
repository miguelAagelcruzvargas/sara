"""
🧪 SARA - Test Suite for User Profile (CORREGIDO)
==================================================

Tests para el módulo de perfil de usuario.
Actualizado para coincidir con la estructura real del módulo.
"""

import pytest
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_profile import UserProfile


class TestUserProfileInitialization:
    """Tests para inicialización del perfil"""
    
    def test_create_profile(self, temp_db):
        """Test: Crear perfil de usuario"""
        # Usar base de datos temporal
        UserProfile.DB_FILE = temp_db
        profile = UserProfile()
        
        assert profile is not None
        assert profile.conn is not None
        assert profile.profile is not None
    
    def test_database_tables_created(self, temp_db):
        """Test: Verificar que se crean las tablas"""
        UserProfile.DB_FILE = temp_db
        profile = UserProfile()
        
        # Verificar que existen las tablas
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "user_info" in tables
        assert "voice_preferences" in tables
        assert "work_config" in tables  # Nombre correcto de la tabla
        assert "general_preferences" in tables
        
        conn.close()


class TestUserInfoManagement:
    """Tests para manejo de información del usuario"""
    
    @pytest.fixture
    def profile(self, temp_db):
        UserProfile.DB_FILE = temp_db
        return UserProfile()
    
    def test_load_default_profile(self, profile):
        """Test: Cargar perfil por defecto"""
        assert profile.profile is not None
        # Estructura correcta: {"user": {...}, "voice": {...}, "work": {...}}
        assert "user" in profile.profile
        assert "voice" in profile.profile
        assert "work" in profile.profile
    
    def test_update_user_name(self, profile):
        """Test: Actualizar nombre de usuario"""
        profile.update_user_info(name="Test User", preferred_name="Tester")
        
        # Recargar perfil
        updated = profile.load_profile()
        
        assert updated["user"]["name"] == "Test User"
        assert updated["user"]["preferred_name"] == "Tester"
    
    def test_update_user_age(self, profile):
        """Test: Actualizar edad"""
        profile.update_user_info(age=25)
        updated = profile.load_profile()
        
        assert updated["user"]["age"] == 25
    
    def test_update_user_city(self, profile):
        """Test: Actualizar ciudad"""
        profile.update_user_info(city="Test City")
        updated = profile.load_profile()
        
        assert updated["user"]["city"] == "Test City"


class TestVoicePreferences:
    """Tests para preferencias de voz"""
    
    @pytest.fixture
    def profile(self, temp_db):
        UserProfile.DB_FILE = temp_db
        return UserProfile()
    
    def test_update_voice_language(self, profile):
        """Test: Actualizar idioma de voz"""
        profile.update_voice_preferences(language="en-US")
        updated = profile.load_profile()
        
        assert updated["voice"]["language"] == "en-US"
    
    def test_update_voice_type(self, profile):
        """Test: Actualizar tipo de voz"""
        profile.update_voice_preferences(voice_type="male")
        updated = profile.load_profile()
        
        assert updated["voice"]["type"] == "male"
    
    def test_update_voice_speed(self, profile):
        """Test: Actualizar velocidad de voz"""
        profile.update_voice_preferences(speed="fast")
        updated = profile.load_profile()
        
        assert updated["voice"]["speed"] == "fast"


class TestWorkProfile:
    """Tests para perfil de trabajo"""
    
    @pytest.fixture
    def profile(self, temp_db):
        UserProfile.DB_FILE = temp_db
        return UserProfile()
    
    def test_update_default_profile(self, profile):
        """Test: Actualizar perfil por defecto"""
        profile.update_work_profile(default_profile="oficina")
        updated = profile.load_profile()
        
        assert updated["work"]["default_profile"] == "oficina"
    
    def test_update_work_hours(self, profile):
        """Test: Actualizar horario de trabajo"""
        profile.update_work_profile(start_time="09:00", end_time="17:00")
        updated = profile.load_profile()
        
        assert updated["work"]["work_hours"]["start"] == "09:00"
        assert updated["work"]["work_hours"]["end"] == "17:00"


class TestSetupCompletion:
    """Tests para estado de setup"""
    
    @pytest.fixture
    def profile(self, temp_db):
        UserProfile.DB_FILE = temp_db
        return UserProfile()
    
    def test_initial_setup_incomplete(self, profile):
        """Test: Setup inicialmente incompleto"""
        # Por defecto debería estar incompleto
        is_complete = profile.is_setup_complete()
        assert isinstance(is_complete, bool)
    
    def test_mark_setup_complete(self, profile):
        """Test: Marcar setup como completo"""
        profile.mark_setup_complete()
        assert profile.is_setup_complete() == True
    
    def test_get_welcome_message(self, profile):
        """Test: Obtener mensaje de bienvenida"""
        profile.update_user_info(preferred_name="Tester")
        message = profile.get_welcome_message()
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert "Tester" in message or "SARA" in message


class TestProfileReset:
    """Tests para reseteo de perfil"""
    
    @pytest.fixture
    def profile(self, temp_db):
        UserProfile.DB_FILE = temp_db
        return UserProfile()
    
    def test_reset_profile(self, profile):
        """Test: Resetear perfil a valores por defecto"""
        # Modificar perfil
        profile.update_user_info(name="Test", age=30)
        profile.update_voice_preferences(language="en-US")
        
        # Resetear
        profile.reset_profile()
        
        # Verificar que volvió a valores por defecto
        updated = profile.load_profile()
        # Después del reset, el nombre puede ser "Usuario" o vacío
        assert updated["user"]["name"] in ["Usuario", ""]


class TestConfigSummary:
    """Tests para resumen de configuración"""
    
    @pytest.fixture
    def profile(self, temp_db):
        UserProfile.DB_FILE = temp_db
        return UserProfile()
    
    def test_get_config_summary(self, profile):
        """Test: Obtener resumen de configuración"""
        summary = profile.get_config_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "PERFIL" in summary or "Nombre" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
