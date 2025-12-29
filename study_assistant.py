import os
import logging
from typing import Optional, List, Tuple
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

class StudyAssistant:
    """Asistente de estudio con resumen de PDFs y generación de flashcards"""
    
    def __init__(self, ia_callback=None):
        """
        Args:
            ia_callback: Función para consultar IA (ej: brain.consultar_ia)
        """
        self.ia_callback = ia_callback
        
    def summarize_pdf(self, file_path: str) -> str:
        """Resume un PDF usando IA"""
        if not PyPDF2:
            return "❌ PyPDF2 no está instalado. Ejecuta: pip install PyPDF2"
        
        if not os.path.exists(file_path):
            return f"❌ Archivo no encontrado: {file_path}"
        
        try:
            # Extraer texto del PDF
            text = self._extract_text_from_pdf(file_path)
            
            if not text.strip():
                return "❌ No se pudo extraer texto del PDF (puede estar protegido o ser imagen)"
            
            # Limitar texto si es muy largo (max 4000 caracteres para IA)
            if len(text) > 4000:
                text = text[:4000] + "..."
            
            # Resumir con IA
            if self.ia_callback:
                prompt = f"""Resume el siguiente documento de forma concisa y estructurada.
Incluye:
- Tema principal
- Puntos clave (máximo 5)
- Conclusión

Documento:
{text}"""
                
                summary, _ = self.ia_callback(prompt)
                return f"📄 Resumen del PDF:\n\n{summary}"
            else:
                return f"📄 Texto extraído ({len(text)} caracteres):\n\n{text[:500]}..."
                
        except Exception as e:
            logging.error(f"Error resumiendo PDF: {e}")
            return f"❌ Error al procesar PDF: {e}"
    
    def generate_flashcards(self, topic: str, count: int = 5) -> str:
        """Genera flashcards sobre un tema usando IA"""
        if not self.ia_callback:
            return "❌ IA no disponible para generar flashcards"
        
        try:
            prompt = f"""Genera {count} flashcards educativas sobre: {topic}

Formato para cada flashcard:
Q: [Pregunta clara y específica]
A: [Respuesta concisa]

Asegúrate de que las preguntas sean variadas (definiciones, ejemplos, aplicaciones, etc.)"""
            
            flashcards, _ = self.ia_callback(prompt)
            
            return f"🃏 Flashcards sobre '{topic}':\n\n{flashcards}\n\n💡 Úsalas para estudiar y memorizar conceptos clave."
            
        except Exception as e:
            logging.error(f"Error generando flashcards: {e}")
            return f"❌ Error generando flashcards: {e}"
    
    def generate_flashcards_from_pdf(self, file_path: str, count: int = 5) -> str:
        """Genera flashcards a partir de un PDF"""
        if not PyPDF2:
            return "❌ PyPDF2 no está instalado"
        
        if not os.path.exists(file_path):
            return f"❌ Archivo no encontrado: {file_path}"
        
        try:
            # Extraer texto
            text = self._extract_text_from_pdf(file_path)
            
            if not text.strip():
                return "❌ No se pudo extraer texto del PDF"
            
            # Limitar texto
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            # Generar flashcards con IA
            if self.ia_callback:
                prompt = f"""Basándote en el siguiente documento, genera {count} flashcards educativas.

Formato:
Q: [Pregunta]
A: [Respuesta]

Documento:
{text}"""
                
                flashcards, _ = self.ia_callback(prompt)
                return f"🃏 Flashcards del PDF:\n\n{flashcards}"
            else:
                return "❌ IA no disponible"
                
        except Exception as e:
            logging.error(f"Error generando flashcards del PDF: {e}")
            return f"❌ Error: {e}"
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extrae texto de un PDF"""
        text = ""
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extraer texto de todas las páginas
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text.strip()
    
    def quiz_mode(self, flashcards_text: str) -> str:
        """Modo interactivo de quiz (para futuro)"""
        # TODO: Implementar modo interactivo
        return "🚧 Modo quiz interactivo en desarrollo"


# Función helper para obtener instancia
_study_assistant_instance = None

def obtener_study_assistant(ia_callback=None):
    """Obtiene o crea la instancia del asistente de estudio"""
    global _study_assistant_instance
    if _study_assistant_instance is None:
        _study_assistant_instance = StudyAssistant(ia_callback)
    return _study_assistant_instance
