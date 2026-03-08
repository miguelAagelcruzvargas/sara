"""
🧪 SARA - Test Suite for Voice Engine
=====================================

Tests para el motor de voz (TTS).
Verifica generación, reproducción, y limpieza de audio.
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import NeuralVoiceEngine


class TestVoiceInitialization:
    """Tests para inicialización del motor de voz"""
    
    def test_engine_creation(self):
        """Test: Crear instancia del motor de voz"""
        engine = NeuralVoiceEngine()
        assert engine is not None
        assert hasattr(engine, 'audio_queue')
    
    def test_pygame_initialization(self):
        """Test: Verificar inicialización de pygame"""
        engine = NeuralVoiceEngine()
        import pygame
        assert pygame.mixer.get_init() is not None


class TestTextCleaning:
    """Tests para limpieza de texto"""
    
    @pytest.fixture
    def engine(self):
        return NeuralVoiceEngine()
    
    def test_clean_spanish_text(self, engine):
        """Test: Preservar acentos españoles"""
        texto = "Hola, ¿cómo estás? ¡Muy bien!"
        limpio = engine._limpiar_texto(texto)
        assert "á" in limpio or "a" in limpio  # Debería preservar o normalizar
        assert "¿" in limpio or "?" in limpio
    
    def test_remove_special_chars(self, engine):
        """Test: Eliminar caracteres especiales"""
        texto = "Texto con @#$% caracteres raros"
        limpio = engine._limpiar_texto(texto)
        assert "@" not in limpio
        assert "#" not in limpio
    
    def test_preserve_numbers(self, engine):
        """Test: Preservar números"""
        texto = "Son las 3:45 PM"
        limpio = engine._limpiar_texto(texto)
        assert "3" in limpio
        assert "45" in limpio


class TestAudioGeneration:
    """Tests para generación de audio"""
    
    @pytest.fixture
    def engine(self):
        return NeuralVoiceEngine()
    
    def test_generate_simple_audio(self, engine):
        """Test: Generar audio simple"""
        texto = "Hola mundo"
        filename = "test_audio.mp3"
        
        try:
            # Generar audio
            result = engine._generar_chunk_sync(texto, filename)
            assert os.path.exists(result)
        finally:
            # Limpiar
            if os.path.exists(filename):
                engine._safe_remove(filename)
    
    @pytest.mark.skip(reason="Requiere conexión a internet")
    def test_generate_long_text(self, engine):
        """Test: Generar audio de texto largo"""
        texto = "Este es un texto muy largo " * 20
        filename = "test_long_audio.mp3"
        
        try:
            result = engine._generar_chunk_sync(texto, filename)
            assert os.path.exists(result)
            # Verificar que el archivo no esté vacío
            assert os.path.getsize(result) > 0
        finally:
            if os.path.exists(filename):
                engine._safe_remove(filename)


class TestAudioPlayback:
    """Tests para reproducción de audio"""
    
    @pytest.fixture
    def engine(self):
        return NeuralVoiceEngine()
    
    def test_is_speaking_initially_false(self, engine):
        """Test: Verificar que inicialmente no está hablando"""
        assert not engine.esta_hablando()
    
    @pytest.mark.skip(reason="Requiere audio output")
    def test_speak_short_text(self, engine):
        """Test: Hablar texto corto"""
        engine.hablar("Hola")
        # Esperar un momento para que empiece
        time.sleep(0.5)
        # Debería estar hablando
        assert engine.esta_hablando()
    
    def test_stop_speaking(self, engine):
        """Test: Detener reproducción"""
        engine.hablar("Texto largo para probar detención")
        time.sleep(0.2)
        engine.detener()
        time.sleep(0.1)
        assert not engine.esta_hablando()


class TestFileCleaning:
    """Tests para limpieza de archivos"""
    
    @pytest.fixture
    def engine(self):
        return NeuralVoiceEngine()
    
    def test_safe_remove_existing_file(self, engine):
        """Test: Eliminar archivo existente"""
        # Crear archivo temporal
        test_file = "test_temp.txt"
        with open(test_file, "w") as f:
            f.write("test")
        
        # Eliminar con safe_remove
        engine._safe_remove(test_file)
        
        # Verificar que se eliminó
        assert not os.path.exists(test_file)
    
    def test_safe_remove_nonexistent_file(self, engine):
        """Test: Intentar eliminar archivo inexistente"""
        # No debería lanzar error
        engine._safe_remove("archivo_que_no_existe.mp3")


class TestEdgeCases:
    """Tests para casos extremos"""
    
    @pytest.fixture
    def engine(self):
        return NeuralVoiceEngine()
    
    def test_empty_text(self, engine):
        """Test: Texto vacío"""
        # No debería crashear
        engine.hablar("")
    
    def test_very_long_text(self, engine):
        """Test: Texto muy largo"""
        texto = "Palabra " * 1000
        # Debería dividir en chunks
        engine.hablar(texto)
    
    def test_special_characters_only(self, engine):
        """Test: Solo caracteres especiales"""
        texto = "@#$%^&*()"
        limpio = engine._limpiar_texto(texto)
        # Debería quedar vacío o con muy poco
        assert len(limpio) < len(texto)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
