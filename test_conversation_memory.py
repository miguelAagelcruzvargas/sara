
import unittest
import os
import json
import tempfile
import shutil
from conversation_memory import ConversationMemory, MEMORY_FILE
from datetime import datetime

class TestConversationMemory(unittest.TestCase):
    
    def setUp(self):
        # Usar un archivo temporal para no sobreescribir el real
        self.test_dir = tempfile.mkdtemp()
        self.original_memory_file = MEMORY_FILE
        self.test_file = os.path.join(self.test_dir, "test_history.json")
        
        # Monkey patch del nombre del archivo (si fuera una variable global accesible, 
        # pero como es importada, mejor sobreescribimos la ruta en runtime si funcionara,
        # pero al ser modulo-level constant es dificil mockear sin patch.
        # Mejor usamos unittest.mock.patch
        pass

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_topic_detection_enhanced(self):
        """Test detection of new topics and flexible keywords"""
        mem = ConversationMemory()
        
        # Música (keywords flexibles)
        self.assertEqual(mem._detect_topic("pon una rola de rock"), "música")
        self.assertEqual(mem._detect_topic("quiero escuchar bad bunny"), "música")
        self.assertEqual(mem._detect_topic("reproducir playlist"), "música")
        
        # Sistema
        self.assertEqual(mem._detect_topic("mi pc está lenta"), "sistema")
        self.assertEqual(mem._detect_topic("baja el brillo"), "sistema")
        
        # Identidad
        self.assertEqual(mem._detect_topic("quien es tu creador"), "identidad")
        
        # Clima
        self.assertEqual(mem._detect_topic("está nublado hoy?"), "clima")
        self.assertEqual(mem._detect_topic("pronostico para mañana"), "clima")

    def test_persistence_flow(self):
        """Test save and load flow using a mock file path"""
        from unittest.mock import patch
        
        # Patch MEMORY_FILE inside conversation_memory module
        with patch('conversation_memory.MEMORY_FILE', self.test_file):
            # 1. Crear memoria y agregar datos
            mem1 = ConversationMemory()
            mem1.add_turn("Hola", "Hola usuario", intent="greeting")
            mem1.add_turn("Pon música", "Reproduciendo...", intent="music_play")
            
            # Verificar que existe archivo
            self.assertTrue(os.path.exists(self.test_file))
            
            # 2. Cargar en nueva instancia
            mem2 = ConversationMemory()
            self.assertEqual(len(mem2.history), 2)
            self.assertEqual(mem2.current_topic, "música")
            self.assertEqual(mem2.history[0]["user"], "Hola")
            
            # 3. Verificar timestamp
            self.assertTrue(isinstance(mem2.history[0]["timestamp"], str))

    def test_clear_memory(self):
        """Test clearing memory updates the file"""
        from unittest.mock import patch
        with patch('conversation_memory.MEMORY_FILE', self.test_file):
            mem = ConversationMemory()
            mem.add_turn("Test", "Response")
            
            mem.clear()
            
            self.assertEqual(len(mem.history), 0)
            self.assertIsNone(mem.current_topic)
            
            # Verificar archivo vacío
            with open(self.test_file, 'r') as f:
                data = json.load(f)
                self.assertEqual(len(data["history"]), 0)

if __name__ == '__main__':
    unittest.main()
