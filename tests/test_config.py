"""
🧪 SARA - Test Suite for Configuration Manager
==============================================

Tests para el gestor de configuración.
Verifica carga, guardado, y validación de configuración.
"""

import pytest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ConfigManager


class TestConfigLoading:
    """Tests para carga de configuración"""
    
    def test_load_default_config(self):
        """Test: Cargar configuración por defecto"""
        config = ConfigManager.cargar_config()
        assert config is not None
        assert isinstance(config, dict)
    
    def test_config_has_provider(self):
        """Test: Configuración tiene proveedor"""
        config = ConfigManager.cargar_config()
        assert "provider" in config
        assert config["provider"] in ["Gemini", "Groq", "ChatGPT"]


class TestConfigSaving:
    """Tests para guardado de configuración"""
    
    def test_save_config(self):
        """Test: Guardar configuración"""
        test_config = {"provider": "Gemini", "test_key": "test_value"}
        result = ConfigManager.guardar_config(test_config)
        assert result is True
    
    def test_config_persistence(self):
        """Test: Persistencia de configuración"""
        # Guardar
        test_data = {"provider": "Groq", "custom_setting": "value"}
        ConfigManager.guardar_config(test_data)
        
        # Cargar
        loaded = ConfigManager.cargar_config()
        assert loaded.get("provider") == "Groq"


class TestAPIKeyManagement:
    """Tests para manejo de API keys"""
    
    def test_api_keys_not_in_json(self):
        """Test: API keys no se guardan en JSON"""
        config = ConfigManager.cargar_config()
        # Las keys deberían estar en .env, no en el JSON
        assert "gemini_key" not in json.dumps(config) or config.get("gemini_key", "").startswith("***")
    
    @pytest.mark.skip(reason="Modifica .env real")
    def test_save_api_keys(self):
        """Test: Guardar API keys en .env"""
        result = ConfigManager.guardar_api_keys(
            gemini_key="test_key_123",
            provider="Gemini"
        )
        assert result is True


class TestConfigValidation:
    """Tests para validación de configuración"""
    
    def test_validate_with_keys(self):
        """Test: Validar configuración con keys"""
        # Este test depende de si hay keys configuradas
        is_valid, message = ConfigManager.validar_configuracion()
        assert isinstance(is_valid, bool)
        assert isinstance(message, str)
    
    def test_needs_initial_setup(self):
        """Test: Verificar si necesita setup inicial"""
        needs_setup = ConfigManager.necesita_configuracion_inicial()
        assert isinstance(needs_setup, bool)


class TestInstructions:
    """Tests para instrucciones de setup"""
    
    def test_get_setup_instructions(self):
        """Test: Obtener instrucciones de setup"""
        instructions = ConfigManager.obtener_instrucciones_setup()
        assert isinstance(instructions, str)
        assert len(instructions) > 0
        assert "API" in instructions or "configuración" in instructions.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
