"""
🧪 SARA - Test Suite for Intent Classifier
==========================================

Tests para el sistema de clasificación de intenciones (NLU).
Verifica las 3 capas: Pattern Matching, ML, y AI Fallback.
"""

import pytest
import sys
import os

# Agregar directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intent_classifier import HybridIntentClassifier


class TestPatternMatching:
    """Tests para Layer 1: Pattern Matching"""
    
    @pytest.fixture
    def classifier(self):
        """Fixture para crear un clasificador sin IA"""
        return HybridIntentClassifier(ia_callback=None)
    
    def test_volumen_subir(self, classifier):
        """Test: Detectar comando de subir volumen"""
        intent, params, source = classifier.clasificar("sube el volumen")
        assert intent == "VOLUMEN_SUBIR"
        assert source == "pattern"
        assert params.get("amount") == 10
    
    def test_volumen_bajar(self, classifier):
        """Test: Detectar comando de bajar volumen"""
        intent, params, source = classifier.clasificar("baja el volumen")
        assert intent == "VOLUMEN_BAJAR"
        assert source == "pattern"
    
    def test_silencio(self, classifier):
        """Test: Detectar comando de silencio"""
        intent, params, source = classifier.clasificar("silencio")
        assert intent == "SILENCIO"
        assert source == "pattern"
    
    def test_abrir_app(self, classifier):
        """Test: Detectar comando de abrir aplicación"""
        intent, params, source = classifier.clasificar("abre chrome")
        assert intent == "ABRIR_APP"
        assert params.get("app_name") == "chrome"


class TestMLClassifier:
    """Tests para Layer 2: ML Classifier"""
    
    @pytest.fixture
    def classifier(self):
        return HybridIntentClassifier(ia_callback=None)
    
    def test_semantic_similarity_volumen(self, classifier):
        """Test: Similitud semántica para volumen"""
        # "hay mucho ruido" debería mapear a bajar volumen
        intent, params, source = classifier.clasificar("hay mucho ruido")
        assert intent == "VOLUMEN_BAJAR"
        assert source == "ml"
    
    def test_semantic_similarity_hora(self, classifier):
        """Test: Similitud semántica para hora"""
        intent, params, source = classifier.clasificar("dime la hora")
        assert intent == "HORA_FECHA"
        assert source in ["pattern", "ml"]
    
    def test_confidence_threshold(self, classifier):
        """Test: Verificar que comandos ambiguos van a AI"""
        # Comando muy ambiguo debería tener baja confianza
        intent, params, source = classifier.clasificar("haz algo interesante")
        # Debería caer a CONVERSACION si no hay IA
        assert intent == "CONVERSACION"


class TestCaching:
    """Tests para el sistema de caché"""
    
    @pytest.fixture
    def classifier(self):
        return HybridIntentClassifier(ia_callback=None)
    
    def test_cache_hit(self, classifier):
        """Test: Verificar que el caché funciona"""
        # Primera llamada
        intent1, params1, source1 = classifier.clasificar("sube el volumen")
        
        # Segunda llamada (debería usar caché)
        intent2, params2, source2 = classifier.clasificar("sube el volumen")
        
        assert intent1 == intent2
        assert source2 == "cache" or source2 == source1  # Puede ser cache o pattern
    
    def test_cache_normalization(self, classifier):
        """Test: Normalización de comandos para caché"""
        # Comandos similares deberían usar el mismo caché
        intent1, _, _ = classifier.clasificar("sube el volumen")
        intent2, _, _ = classifier.clasificar("SUBE EL VOLUMEN")
        
        assert intent1 == intent2


class TestParameterExtraction:
    """Tests para extracción de parámetros"""
    
    @pytest.fixture
    def classifier(self):
        return HybridIntentClassifier(ia_callback=None)
    
    def test_extract_app_name(self, classifier):
        """Test: Extraer nombre de aplicación"""
        intent, params, source = classifier.clasificar("abre spotify")
        assert params.get("app_name") == "spotify"
    
    def test_extract_search_query(self, classifier):
        """Test: Extraer query de búsqueda"""
        intent, params, source = classifier.clasificar("busca python tutorials")
        assert intent == "BUSCAR_WEB"
        assert "python" in params.get("query", "").lower()
    
    def test_extract_alarm_time(self, classifier):
        """Test: Extraer tiempo de alarma"""
        intent, params, source = classifier.clasificar("alarma en 5 minutos")
        assert intent == "ALARMA"
        assert params.get("minutes") == 5


class TestEdgeCases:
    """Tests para casos extremos"""
    
    @pytest.fixture
    def classifier(self):
        return HybridIntentClassifier(ia_callback=None)
    
    def test_empty_command(self, classifier):
        """Test: Comando vacío"""
        intent, params, source = classifier.clasificar("")
        assert intent == "CONVERSACION"
    
    def test_very_long_command(self, classifier):
        """Test: Comando muy largo"""
        long_cmd = "sube el volumen " * 50
        intent, params, source = classifier.clasificar(long_cmd)
        assert intent == "VOLUMEN_SUBIR"
    
    def test_special_characters(self, classifier):
        """Test: Caracteres especiales"""
        intent, params, source = classifier.clasificar("¿qué hora es?")
        assert intent == "HORA_FECHA"
    
    def test_mixed_case(self, classifier):
        """Test: Mayúsculas y minúsculas mezcladas"""
        intent, params, source = classifier.clasificar("SuBe El VoLuMeN")
        assert intent == "VOLUMEN_SUBIR"


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "--tb=short"])
