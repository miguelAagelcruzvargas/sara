"""
Test Visual: Cómo se ven las funciones de estudio en la interfaz de SARA
"""
import sys
import os

# Asegurarse de que podemos importar desde el directorio actual
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simular_comandos_estudio():
    """
    Simula comandos de estudio para ver cómo se muestran en la interfaz
    """
    print("="*70)
    print("   SIMULACIÓN: Comandos de Estudio en SARA")
    print("="*70)
    print()
    
    comandos_test = [
        ("💬 Usuario", "modo estudio"),
        ("🤖 SARA", """📚 **Modo Estudio Activado**

Estoy lista para ayudarte. Puedes decirme:
• 'Resume este PDF [ruta]'
• 'Resume este video [YouTube URL]'
• 'Crea flashcards de [tema o video]'
• 'Hazme un quiz'
💡 ¿Por dónde empezamos?"""),
        
        ("💬 Usuario", "genera examen de Python"),
        ("🤖 SARA", """📝 **EXAMEN DE PYTHON**

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
**RESPUESTAS:**
1. b) Python es interpretado
2. Verdadero - Python tiene tipado dinámico pero fuerte
3. Data Science, Web Development, Automatización, IA"""),
        
        ("💬 Usuario", "resumen simple de Machine Learning"),
        ("🤖 SARA", """📚 **Resumen Nivel SIMPLE:**

**Idea Principal:**
Machine Learning es como enseñarle a una computadora a aprender de ejemplos, igual que tú aprendes de la práctica.

**Puntos Clave:**
1. La computadora aprende patrones (como reconocer fotos de gatos)
2. Mientras más ejemplos le des, mejor aprende
3. Se usa en Netflix (recomendaciones), Siri (voz), y videojuegos

**Conclusión:**
Es la forma en que las computadoras se vuelven "inteligentes" sin que les digas exactamente qué hacer."""),
        
        ("💬 Usuario", "resumen técnico de Machine Learning"),
        ("🤖 SARA", """📚 **Resumen Nivel ADVANCED:**

**Idea Principal:**
ML es un subcampo de IA enfocado en algoritmos que mejoran automáticamente mediante experiencia.

**Puntos Clave:**
1. Paradigmas: Supervisado, No Supervisado, Refuerzo
2. Algoritmos clave: Gradient Descent, Backpropagation, SGD
3. Frameworks: TensorFlow, PyTorch, Scikit-learn
4. Métricas: Accuracy, Precision, Recall, F1-Score, AUC-ROC
5. Challenges: Overfitting, Bias-Variance Tradeoff, Feature Engineering

**Conclusión:**
Fundamental para sistemas de producción en computer vision, NLP y sistemas de recomendación."""),
    ]
    
    for emisor, mensaje in comandos_test:
        print(f"\n{emisor}:")
        print("-" * 70)
        print(mensaje)
        print()
    
    print("="*70)
    print("   CARACTERÍSTICAS VISUALES EN LA INTERFAZ:")
    print("="*70)
    print("""
✨ Cómo se ve en SARA:

1. **Área de Chat (CTkTextbox)**
   - Fondo oscuro elegante (#1E293B)
   - Texto del usuario en color púrpura (#8B5CF6)
   - Respuestas de SARA en cyan brillante (#00E5FF)
   - Negritas con ** se renderizan correctamente
   - Scroll suave con barra cyan

2. **Entrada de Comandos**
   - Campo de texto con placeholder "Escribe o habla..."
   - Botón de micrófono 🎤 para voz
   - Botón "Enviar" en cyan brillante
   - Bordes redondeados (12px)

3. **Formato de Mensajes**
   - Timestamp a la izquierda [HH:MM]
   - Emisor en negrita
   - Contenido con markdown básico
   - Separación clara entre mensajes

4. **Pestañas Disponibles**
   💬 Chat - Conversación principal
   ⚙️ Config - Configuración de IA
   🛠️ Dev - Herramientas de desarrollo
   🌐 Network - Monitor de red

5. **Header Superior**
   - Logo "SARA" en cyan
   - Versión en gris
   - Estado (● ONLINE) en verde/rojo
   - Fondo oscuro (#1E293B)
""")
    
    print("\n" + "="*70)
    print("   PRUEBA COMPLETA")
    print("="*70)
    print("""
Para ver esto en acción:
1. Ejecuta: python sara.py
2. Escribe cualquiera de estos comandos:
   - "modo estudio"
   - "genera examen de [tema]"
   - "resumen simple de [tema]"
   - "resumen técnico de [tema]"
   - "crea flashcards de [tema]"

Las respuestas aparecerán con el formato mostrado arriba.
""")

if __name__ == "__main__":
    simular_comandos_estudio()
