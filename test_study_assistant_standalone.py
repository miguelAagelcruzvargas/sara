
import unittest
from unittest.mock import MagicMock
import sys
import os

# Ad paths to sys.path to find modules
sys.path.append(os.getcwd())

from study_assistant import StudyAssistant, obtener_study_assistant

class TestStudyAssistant(unittest.TestCase):
    def setUp(self):
        # Mock callback
        self.mock_ai = MagicMock(return_value=("Mocked AI Response", "Mocked Metadata"))
        self.assistant = StudyAssistant(ia_callback=self.mock_ai)

    def test_instantiation(self):
        self.assertIsInstance(self.assistant, StudyAssistant)
        print("\n[OK] Instantiation successful")

    def test_generate_flashcards(self):
        topic = "Python Programming"
        result = self.assistant.generate_flashcards(topic, count=3)
        
        # Verify call arguments
        args, _ = self.mock_ai.call_args
        self.assertIn("Python Programming", args[0])
        self.assertIn("flashcards", args[0])
        
        # Verify output
        self.assertIn("Mocked AI Response", result)
        print("\n[OK] Flashcard generation test passed")

    def test_pypdf2_dependency(self):
        import study_assistant
        if study_assistant.PyPDF2 is None:
            print("\n[WARNING] PyPDF2 is NOT installed. PDF features will fail.")
        else:
            print("\n[OK] PyPDF2 is installed and available.")

if __name__ == "__main__":
    unittest.main()
