import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mocks para dependencias pesadas
sys.modules['customtkinter'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['pyaudio'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numpy.linalg'] = MagicMock() # FIX
sys.modules['matplotlib'] = MagicMock() # FIX
sys.modules['matplotlib.pyplot'] = MagicMock() # FIX
sys.modules['mediapipe'] = MagicMock() # FIX - Bypass heavy lib
sys.modules['cv2'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock() # FIX: Mock submodule
sys.modules['google.generativeai'] = MagicMock()
sys.modules['psutil'] = MagicMock()

# Ahora importamos brain
from brain import SaraBrain

class TestSaraBrainRefactor(unittest.TestCase):
    def setUp(self):
        # Mock de dependencias internas
        self.mock_config_manager = MagicMock()
        self.mock_config_manager.cargar_config.return_value = {"provider": "Gemini"}
        
        with patch('brain.ConfigManager', self.mock_config_manager), \
             patch('brain.NeuralVoiceEngine', MagicMock()), \
             patch('brain.DevOpsManager', MagicMock()), \
             patch('brain.SystemMonitor', MagicMock()), \
             patch('brain.MemoryManager', MagicMock()), \
             patch('brain.CronosManager', MagicMock()), \
             patch('brain.HybridIntentClassifier', MagicMock()) as MockNLU, \
             patch('brain.SecondBrain', MagicMock()), \
             patch('brain.SaraWebSurfer', MagicMock()), \
             patch('brain.ConversationMemory', MagicMock()) as MockMem:
            
            self.brain = SaraBrain()
            self.mock_nlu = self.brain.intent_classifier
            self.mock_memory = self.brain.memory
            # Mock de handlers
            self.brain.second_brain.memorizar.return_value = "Memorizado"
            self.brain.sys_control = MagicMock()
            
    def test_initialization_handlers(self):
        """Verificar que los handlers se inicializaron correctamente"""
        self.assertTrue(hasattr(self.brain, 'handlers'))
        self.assertIn('MEMORIZAR', self.brain.handlers)
        self.assertIn('VOLUMEN_SUBIR', self.brain.handlers)
        self.assertIn('BUSCAR_WEB', self.brain.handlers)

    def test_procesar_nlu_hit(self):
        """Verificar flujo NLU -> Handler -> Memoria"""
        # Configurar NLU mock
        self.mock_nlu.clasificar.return_value = ("MEMORIZAR", {"data": "mi clave"}, "pattern")
        
        # Ejecutar
        respuesta, origen = self.brain.procesar("memoriza mi clave")
        
        # Verificar llamadas
        self.mock_nlu.clasificar.assert_called_with("memoriza mi clave")
        self.brain.second_brain.memorizar.assert_called_with("mi clave")
        self.mock_memory.add_turn.assert_called()
        self.assertEqual(origen, "sara")
        self.assertIn("Memorizado", respuesta)

    def test_procesar_fallback_router(self):
        """Verificar flujo NLU Miss -> AI Router (IA Online)"""
        # Configurar NLU miss
        self.mock_nlu.clasificar.return_value = ("CONVERSACION", {}, "fallback")
        self.brain.ia_online = True
        self.brain.consultar_ia = MagicMock(return_value=("Hola amigo", "ai"))
        
        # Ejecutar
        respuesta, origen = self.brain.procesar("hola sara")
        
        # Verificar llamadas
        self.brain.consultar_ia.assert_called()
        self.mock_memory.add_turn.assert_called()
        self.assertEqual(origen, "ai")
        self.assertEqual(respuesta, "Hola amigo")

    def test_procesar_fallback_offline(self):
        """Verificar flujo NLU Miss -> IA Offline -> Fallback Msg"""
        # Configurar NLU miss y IA offline
        self.mock_nlu.clasificar.return_value = ("CONVERSACION", {}, "fallback")
        self.brain.ia_online = False
        
        # Ejecutar
        respuesta, origen = self.brain.procesar("blabla")
        
        # Verificar
        self.assertIn("No te entendí", respuesta)
        self.assertEqual(origen, "sara")

if __name__ == '__main__':
    unittest.main()
