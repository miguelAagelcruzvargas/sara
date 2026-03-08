import unittest
from sara_knowledge import SaraKnowledge

class TestSaraKnowledge(unittest.TestCase):
    
    def test_smart_response_identity(self):
        """Test identity questions"""
        response = SaraKnowledge.smart_response("quien eres")
        self.assertIsNotNone(response)
        self.assertIn("SARA", response)

    def test_smart_response_pc_cleaning_strict(self):
        """Test current PC cleaning keywords (should pass)"""
        response = SaraKnowledge.smart_response("limpieza de sistema")
        self.assertIsNotNone(response)
        self.assertIn("SISTEMA", response)
        
    def test_smart_response_pc_cleaning_flexible(self):
        """Test flexible PC cleaning keywords (likely to fail currently)"""
        # User example: "Necesito que limpies mi PC"
        # Current code checks for: "sistema", "limpieza", "optimiza"
        # "limpies" matches none of these strings exactly.
        response = SaraKnowledge.smart_response("necesito que limpies mi pc")
        self.assertIsNotNone(response, "Should handle 'limpies' as a synonym for cleaning")
        self.assertIn("SISTEMA", response)
        
    def test_smart_response_gaming_flexible(self):
        """Test flexible gaming keywords"""
        # "quiero jugar algo" -> might fail if "jugar" isn't strictly "juego" or "gaming"
        # Code checks: "juego", "gaming", "valorant"
        response = SaraKnowledge.smart_response("quiero jugar algo")
        self.assertIsNotNone(response, "Should handle 'jugar' verb form")
        self.assertIn("GAMING", response)

if __name__ == '__main__':
    unittest.main()
