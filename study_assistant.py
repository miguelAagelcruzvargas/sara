import os
import logging
import json
from typing import Optional, List, Dict, Tuple, Any

# Intentamos importar pypdf
try:
    import pypdf
except ImportError:
    pypdf = None

# Intentamos importar youtube_transcript_api
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

class StudyAssistant:
    """
    Asistente de estudio avanzado.
    Capacidades: Resumen de documentos, generación de flashcards estructuradas y modo quiz.
    """
    
    def __init__(self, ia_callback=None):
        """
        Args:
            ia_callback: Función (prompt) -> (respuesta_texto, tokens)
        """
        self.ia_callback = ia_callback
        # Configuración básica de log
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    def summarize_pdf(self, file_path: str) -> str:
        """Lee un PDF y devuelve un resumen en texto plano."""
        try:
            text = self._prepare_text_input(file_path, is_file=True)
            
            # Recorte seguro para contexto (ajustar según token limit de tu IA)
            # TODO: Para documentos muy largos, implementar "Map-Reduce" (resumir por partes)
            text_context = text[:4000] 
            
            if not self.ia_callback:
                return f"⚠️ IA no conectada. Texto extraído ({len(text)} caracteres):\n{text[:500]}..."

            prompt = f"""
            Actúa como un profesor experto. Resume el siguiente texto extraído de un documento.
            Estructura:
            1. Concepto Central
            2. 3-5 Puntos Clave
            3. Conclusión Práctica

            Texto:
            {text_context}
            """
            
            summary, _ = self.ia_callback(prompt)
            return summary

        except Exception as e:
            logging.error(f"Error en summarize_pdf: {e}")
            return f"❌ Error generando resumen: {str(e)}"

    def generate_flashcards(self, source: str, count: int = 5, is_file: bool = False) -> List[Dict[str, str]]:
        """
        Genera una lista de diccionarios de flashcards.
        Devuelve: [{'q': 'pregunta', 'a': 'respuesta'}, ...]
        """
        if not self.ia_callback:
            logging.warning("IA no disponible")
            return []

        try:
            # Preparamos el contexto (sea archivo o tema libre)
            context_text = self._prepare_text_input(source, is_file)
            
            # Limitamos contexto para evitar errores de API
            context_text = context_text[:3500]

            prompt = f"""
            Genera {count} flashcards educativas de alto nivel basadas en este contexto:
            ---
            {context_text}
            ---
            
            INSTRUCCIONES CRÍTICAS:
            1. Responde ÚNICAMENTE con un JSON válido.
            2. No incluyas texto antes ni después del JSON (sin markdown ```json).
            3. Formato exacto:
            [
                {{"q": "Pregunta clara...", "a": "Respuesta concisa..."}},
                {{"q": "Pregunta...", "a": "Respuesta..."}}
            ]
            """
            
            raw_response, _ = self.ia_callback(prompt)
            return self._parse_json_response(raw_response)

        except Exception as e:
            logging.error(f"Error generando flashcards: {e}")
            return []

    def generate_exam(self, source: str, num_questions: int = 10, is_file: bool = False, exam_type: str = "mixed") -> str:
        """
        Genera un examen completo con preguntas de diferentes tipos.
        
        Args:
            source: Tema o archivo fuente
            num_questions: Número de preguntas
            is_file: Si source es un archivo
            exam_type: 'multiple_choice', 'true_false', 'short_answer', 'mixed'
        
        Returns:
            Examen formateado en texto
        """
        if not self.ia_callback:
            return "❌ IA no disponible para generar examen."
        
        try:
            context_text = self._prepare_text_input(source, is_file)[:4000]
            
            type_instructions = {
                "multiple_choice": "opción múltiple (4 opciones, 1 correcta)",
                "true_false": "verdadero o falso",
                "short_answer": "respuesta corta",
                "mixed": "mixtas (opción múltiple, verdadero/falso y respuesta corta)"
            }
            
            prompt = f"""
            Genera un examen de {num_questions} preguntas tipo {type_instructions.get(exam_type, 'mixtas')} basado en:
            ---
            {context_text}
            ---
            
            Formato:
            1. [Pregunta]
               a) Opción 1
               b) Opción 2
               c) Opción 3
               d) Opción 4
            
            Al final incluye una sección "RESPUESTAS" con las soluciones y breves explicaciones.
            """
            
            exam, _ = self.ia_callback(prompt)
            return exam
            
        except Exception as e:
            logging.error(f"Error generando examen: {e}")
            return f"❌ Error: {str(e)}"
    
    def summarize_by_level(self, source: str, level: str = "intermediate", is_file: bool = False) -> str:
        """
        Genera resumen adaptado al nivel del estudiante.
        
        Args:
            source: Contenido a resumir
            level: 'simple', 'intermediate', 'advanced'
            is_file: Si source es archivo
        """
        if not self.ia_callback:
            return "❌ IA no disponible."
        
        try:
            text = self._prepare_text_input(source, is_file)[:4000]
            
            level_prompts = {
                "simple": "Explica esto como si fuera para un niño de 10 años. Usa analogías simples y evita tecnicismos.",
                "intermediate": "Resume esto para un estudiante de preparatoria/universidad. Usa terminología técnica pero explícala.",
                "advanced": "Resume esto para un experto. Usa terminología avanzada y enfócate en detalles técnicos profundos."
            }
            
            instruction = level_prompts.get(level, level_prompts["intermediate"])
            
            prompt = f"""
            {instruction}
            
            Contenido:
            ---
            {text}
            ---
            
            Estructura tu respuesta en:
            1. Idea Principal
            2. Puntos Clave (3-5)
            3. Conclusión
            """
            
            summary, _ = self.ia_callback(prompt)
            return f"📚 Resumen Nivel {level.upper()}:\n\n{summary}"
            
        except Exception as e:
            logging.error(f"Error en resumen por nivel: {e}")
            return f"❌ Error: {str(e)}"

    def quiz_mode(self, flashcards: List[Dict[str, str]], timed: bool = False, time_per_question: int = 30):
        """
        Ejecuta un quiz interactivo mejorado con estadísticas.
        
        Args:
            flashcards: Lista de flashcards
            timed: Si activar temporizador
            time_per_question: Segundos por pregunta (si timed=True)
        """
        import time
        
        if not flashcards:
            print("⚠️ No hay flashcards cargadas.")
            return

        print(f"\n🎓 --- MODO QUIZ MEJORADO ({len(flashcards)} preguntas) ---")
        if timed:
            print(f"⏱️  Tiempo por pregunta: {time_per_question}s")
        print("Instrucciones: Piensa la respuesta y presiona Enter.\n")
        
        score = 0
        start_time = time.time()
        
        for i, card in enumerate(flashcards, 1):
            q_start = time.time()
            print(f"\n🃏 Pregunta {i}/{len(flashcards)}: {card.get('q', 'Sin pregunta')}")
            
            if timed:
                print(f"⏱️  Tienes {time_per_question} segundos...")
            
            input("   (Presiona Enter para ver respuesta...)")
            q_time = time.time() - q_start
            
            print(f"💡 Respuesta: {card.get('a', 'Sin respuesta')}")
            print(f"⏱️  Tiempo: {q_time:.1f}s")
            
            feedback = input("   ¿Acertaste? (s/n): ").lower()
            if feedback.startswith('s'):
                score += 1
                print("✅ ¡Correcto!")
            else:
                print("❌ Revisa este concepto")
            print("-" * 50)
        
        total_time = time.time() - start_time
        percentage = (score / len(flashcards)) * 100
        
        print(f"\n{'='*50}")
        print(f"🏆 RESULTADOS FINALES")
        print(f"{'='*50}")
        print(f"✅ Aciertos: {score}/{len(flashcards)} ({percentage:.1f}%)")
        print(f"⏱️  Tiempo total: {total_time:.1f}s")
        print(f"⚡ Promedio por pregunta: {total_time/len(flashcards):.1f}s")
        
        if percentage >= 90:
            print("\n🌟 ¡EXCELENTE! Dominas el tema.")
        elif percentage >= 70:
            print("\n👍 ¡BIEN! Sigue practicando.")
        else:
            print("\n📖 Necesitas repasar más este tema.")
        
        print(f"{'='*50}\n")

    # --- MÉTODOS PRIVADOS Y HELPERS ---

    def _prepare_text_input(self, source: str, is_file: bool) -> str:
        """Maneja la lógica de obtener texto ya sea de un string o de un PDF."""
        # 1. Chequeo prioritario de YouTube (URL)
        if "youtube.com" in source or "youtu.be" in source:
            return self._extract_text_from_youtube(source)

        if not is_file:
            return source # Es un tema o texto directo

        # Es un archivo

        # Es un archivo
        if not pypdf:
            raise ImportError("La librería 'pypdf' no está instalada. Ejecuta: pip install pypdf")
        
        if not os.path.exists(source):
            raise FileNotFoundError(f"Archivo no encontrado: {source}")

        return self._extract_text_from_pdf(source)

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extrae texto robustamente usando pypdf."""
        text_content = []
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                # Check de encriptación básico
                if reader.is_encrypted:
                    try:
                        reader.decrypt("") # Intenta contraseña vacía
                    except:
                        raise ValueError("El PDF está encriptado y requiere contraseña.")

                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content.append(extracted)
            
            full_text = "\n".join(text_content).strip()
            
            if not full_text:
                raise ValueError("Se leyó el PDF pero no contenía texto extraíble (quizás es una imagen escaneada).")
                
            return full_text
            
        except Exception as e:
            raise RuntimeError(f"Fallo al leer PDF: {e}")

    def _extract_text_from_youtube(self, url: str) -> str:
        """Extrae transcripción de un video de YouTube."""
        if not YouTubeTranscriptApi:
            raise ImportError("La librería 'youtube-transcript-api' no está instalada. Ejecuta: pip install youtube-transcript-api")
        
        try:
            # Extraer ID del video
            video_id = ""
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be" in url:
                video_id = url.split("/")[-1]
            
            if not video_id:
                raise ValueError("No se pudo identificar el ID del video.")
            
            # Obtener transcripción usando instancia
            yt = YouTubeTranscriptApi()
            transcript = yt.fetch(video_id)
            
            # Iterar sobre snippets
            full_text = " ".join([s.text for s in transcript.snippets])
            return full_text
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detectar si es por falta de subtítulos
            if "transcript" in error_msg or "subtitles" in error_msg or "no transcript" in error_msg:
                raise RuntimeError(
                    "⚠️ Este video no tiene subtítulos disponibles.\n\n"
                    "🔧 FUNCIÓN EN DESARROLLO:\n"
                    "Estamos trabajando en soporte para transcripción automática de audio (Whisper AI).\n"
                    "Por ahora, usa videos que tengan subtítulos activados."
                )
            
            # Otro tipo de error
            raise RuntimeError(f"Fallo al obtener subtítulos de YouTube: {e}")

    def _parse_json_response(self, raw_text: str) -> List[Dict]:
        """Intenta limpiar y parsear la respuesta de la IA a JSON."""
        try:
            # Limpieza común: a veces la IA envuelve en ```json ... ```
            cleaned = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logging.error(f"Fallo al parsear JSON. Texto recibido: {raw_text[:100]}...")
            return []

# --- FACTORY FUNCTION PARA BRAIN.PY ---

def obtener_study_assistant(ia_callback=None):
    """
    Factory function para crear una instancia de StudyAssistant.
    Usado por brain.py para lazy loading.
    """
    return StudyAssistant(ia_callback=ia_callback)

# --- EJEMPLO DE USO (Simulación) ---

if __name__ == "__main__":
    # 1. Definimos un callback de IA simulado (Mock) para probar sin gastar tokens
    def mock_ia_callback(prompt):
        # Simula comportamiento dependiendo de qué pida el prompt
        if "JSON" in prompt:
            return ('[{"q": "¿Qué es Python?", "a": "Un lenguaje de programación."}, '
                    '{"q": "¿Qué es pypdf?", "a": "Una librería para manipular PDFs."}]', 0)
        return ("Este es un resumen simulado del documento...", 0)

    # 2. Inicializamos
    assistant = StudyAssistant(ia_callback=mock_ia_callback)

    # 3. Probamos generación de Flashcards (Tema libre)
    print("--- Generando Flashcards ---")
    cards = assistant.generate_flashcards("Programación en Python", count=2)
    
    # 4. Probamos el Quiz Mode
    assistant.quiz_mode(cards)

    # Nota: Para probar con PDF real:
    # assistant.summarize_pdf("ruta/a/tu/documento.pdf")