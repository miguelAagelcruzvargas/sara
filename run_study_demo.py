import sys
import os
import time
from unittest.mock import MagicMock

# --- CONFIGURACIÓN DE SIMULACIÓN ---
# Simulamos pypdf para no necesitar un PDF real complejo
mock_pypdf = MagicMock()
sys.modules["pypdf"] = mock_pypdf

# Configurar el lector simulado
mock_reader = MagicMock()
mock_page = MagicMock()
mock_page.extract_text.return_value = """
INTRODUCCIÓN A LA INTELIGENCIA ARTIFICIAL
La Inteligencia Artificial (IA) es la simulación de procesos de inteligencia humana.
"""
mock_reader.pages = [mock_page]
mock_pypdf.PdfReader.return_value = mock_reader

# --- IMPORTAR MÓDULO REAL ---
# Añadir directorio actual al path
sys.path.append(os.getcwd())
from study_assistant import StudyAssistant

# --- SIMULADOR DE CEREBRO (IA) ---
def mock_brain_callback(prompt):
    print(f"\n[SARA (Cerebro)]: Recibí solicitud de IA...")
    time.sleep(1) # Simular proceso
    
    if "flashcards" in prompt.lower():
        # Devuelve JSON válido como string, que es lo que espera study_assistant antes de parsearlo
        return """
[
    {"q": "¿Qué es la Inteligencia Artificial?", "a": "Simulación de procesos de inteligencia humana por sistemas informáticos."},
    {"q": "¿Cuáles son los dos tipos principales de IA?", "a": "IA Débil (tarea específica) y IA Fuerte (capacidades generales)."},
    {"q": "Menciona tres aplicaciones de la IA.", "a": "Visión por computadora, NLP y Robótica."}
]
""", "study"
    
    elif "resume" in prompt.lower():
        return """
**Tema Principal:** Introducción a la Inteligencia Artificial

**Puntos Clave:**
1. Definición de IA como simulación de inteligencia humana.
2. Clasificación en IA Débil (específica) y Fuerte (general).
3. Aplicaciones clave: Visión, NLP, Robótica.

**Conclusión:**
La IA abarca desde asistentes simples hasta sistemas complejos que imitan el razonamiento humano.
""", "study"
    
    return "Respuesta genérica", "study"

# --- EJECUCIÓN DEL DEMO ---
def main():
    print("="*50)
    print("   PRUEBA DE FUNCIONALIDAD: SARA STUDY ASSISTANT")
    print("="*50)
    
    # 1. Inicialización
    print("\n1️⃣  Inicializando Asistente...")
    assistant = StudyAssistant(ia_callback=mock_brain_callback)
    print("✅ Asistente listo.")
    
    # 2. Prueba de Flashcards
    topic = "Python"
    print(f"\n2️⃣  Generando Flashcards sobre 'Intergencia Artificial' (Simulación)...")
    print(f"   [Input]: Generar flashcards")
    
    resultado = assistant.generate_flashcards("Inteligencia Artificial", count=3)
    
    print("\n   [Resultado]:")
    print("-" * 30)
    for card in resultado:
        print(f"Q: {card.get('q')}")
        print(f"A: {card.get('a')}")
        print("")
    print("-" * 30)
    
    # 3. Prueba de Resumen PDF
    print(f"\n3️⃣  Resumiendo PDF simulado 'documento.pdf'...")
    # Crear archivo dummy para que os.path.exists no falle
    with open("dummy_test.pdf", "w") as f: f.write("dummy content")
    
    try:
        resultado_pdf = assistant.summarize_pdf("dummy_test.pdf")
        print("\n   [Resultado]:")
        print("-" * 30)
        print(resultado_pdf)
        print("-" * 30)
    finally:
        if os.path.exists("dummy_test.pdf"):
            os.remove("dummy_test.pdf")

    print(f"\n{'-'*21}")
    
    # --- PRUEBA 3: RESUMEN DE YOUTUBE (REAL) ---
    youtube_url = "https://www.youtube.com/watch?v=x7X9w_GIm1s" # What is Python? in 100 Seconds
    print(f"🎬 Probando YouTube: {youtube_url}")
    print("   (Esto conectará a internet para bajar subtítulos real-time)")
    
    try:
        summary_yt = assistant.summarize_pdf(youtube_url) # Usamos la misma función polimórfica o la nueva si la expusimos
        # Nota: En study_assistant.py, _prepare_text_input maneja la URL, así que llamar a summarize_pdf funciona.
        # Pero semanticamente sería mejor tener un método 'summarize' genérico, pero por ahora usamos ese.
        print("\n📝 Resultado del Resumen de Video:")
        print(summary_yt[:500] + "..." if len(summary_yt) > 500 else summary_yt)
    except Exception as e:
        print(f"\n❌ Error en prueba YouTube: {e}")

    print(f"\n{'='*21}")
    print("✅ PRUEBA FINALIZADA EXITOSAMENTE")
    print(f"{'='*21}")

if __name__ == "__main__":
    main()
