"""
Demo de las 3 nuevas funciones premium del Study Assistant
"""
import sys
sys.path.insert(0, '.')

from study_assistant import StudyAssistant

def mock_ia_callback(prompt):
    """Mock de IA para testing"""
    if "JSON" in prompt or "flashcards" in prompt.lower():
        return ('[{"q": "¿Qué es Python?", "a": "Lenguaje de programación interpretado"}]', 0)
    elif "examen" in prompt.lower() or "test" in prompt.lower():
        return ("""
EXAMEN DE PYTHON

1. ¿Cuál es la principal característica de Python?
   a) Compilado
   b) Interpretado ✓
   c) Ensamblador
   d) Binario

2. ¿Python es fuertemente tipado?
   Verdadero ✓

3. Menciona 2 usos principales de Python
   Respuesta: Data Science y Web Development

---
RESPUESTAS:
1. b) Python es interpretado
2. Verdadero - Python tiene tipado dinámico pero fuerte
3. Data Science, Web Development, Automatización, IA
""", 0)
    elif "simple" in prompt.lower() or "niño" in prompt.lower():
        return ("""
📚 RESUMEN SIMPLE

**Idea Principal:**
Python es como un idioma que le hablas a la computadora para que haga cosas.

**Puntos Clave:**
1. Es fácil de aprender (como hablar español)
2. Puedes hacer juegos, páginas web y robots
3. Muchas empresas lo usan (Google, Netflix)

**Conclusión:**
Python es perfecto para empezar a programar porque es simple y poderoso.
""", 0)
    elif "avanzado" in prompt.lower() or "experto" in prompt.lower():
        return ("""
📚 RESUMEN AVANZADO

**Idea Principal:**
Python es un lenguaje interpretado, dinámicamente tipado con GIL (Global Interpreter Lock).

**Puntos Clave:**
1. Paradigma multi-paradigma (OOP, funcional, imperativo)
2. CPython usa reference counting + generational GC
3. Extensible vía C/C++ para performance crítico
4. Ecosistema robusto: NumPy, Pandas, TensorFlow
5. Async/await para concurrencia (asyncio)

**Conclusión:**
Ideal para prototipado rápido y producción en data-intensive applications.
""", 0)
    else:
        return ("Resumen genérico del tema solicitado.", 0)

def main():
    print("="*60)
    print("   DEMO: FUNCIONES PREMIUM - STUDY ASSISTANT")
    print("="*60)
    
    assistant = StudyAssistant(ia_callback=mock_ia_callback)
    
    # --- TEST 1: GENERADOR DE EXÁMENES ---
    print("\n📝 TEST 1: GENERADOR DE EXÁMENES")
    print("-" * 60)
    exam = assistant.generate_exam("Python", num_questions=3, exam_type="mixed")
    print(exam)
    
    # --- TEST 2: RESUMEN SIMPLE ---
    print("\n\n👶 TEST 2: RESUMEN NIVEL SIMPLE")
    print("-" * 60)
    simple_summary = assistant.summarize_by_level("Python", level="simple")
    print(simple_summary)
    
    # --- TEST 3: RESUMEN AVANZADO ---
    print("\n\n🎓 TEST 3: RESUMEN NIVEL AVANZADO")
    print("-" * 60)
    advanced_summary = assistant.summarize_by_level("Python", level="advanced")
    print(advanced_summary)
    
    # --- TEST 4: QUIZ MEJORADO ---
    print("\n\n🎯 TEST 4: QUIZ MODE MEJORADO (con timer)")
    print("-" * 60)
    flashcards = assistant.generate_flashcards("Python", count=2)
    print(f"Flashcards generadas: {len(flashcards)}")
    print("\n⚠️ Nota: El quiz interactivo requiere input del usuario.")
    print("Para probarlo, descomenta la siguiente línea:\n")
    print("# assistant.quiz_mode(flashcards, timed=True, time_per_question=10)")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    main()
