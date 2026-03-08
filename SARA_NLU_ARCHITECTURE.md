# 🧠 Arquitectura NLU Híbrida de SARA 2.0

Este documento detalla la implementación del sistema de Entendimiento del Lenguaje Natural (NLU) de SARA, diseñado para ser rápido, privado y extremadamente robusto.

## 🌟 Resumen de las 3 Capas

SARA utiliza un sistema de **3 capas** para clasificar lo que el usuario quiere decir. Las capas se ejecutan en orden secuencial por prioridad.

| Capa | Tecnología | Velocidad | Función Principal | Conexión |
| :--- | :--- | :--- | :--- | :--- |
| **1. Patrón** | Python (Regex/Keywords) | ~0ms (Instantáneo) | Comandos críticos y repetitivos (Volumen, Silencio) | 📴 Offline |
| **2. ML Local** | `sentence-transformers` | ~50ms (Muy rápido) | Comandos semánticos y variaciones naturales | 📴 Offline |
| **3. IA Gran Modelo** | Gemini / Groq / OpenAI | ~1-2s (Lento) | Casos complejos, ambigüedad extrema o charla | 🌐 Online |

---

## 🔍 Detalle de Implementación

### 1. Capa de Patrón (Pattern Matching)
**Objetivo:** Velocidad máxima y seguridad para comandos de sistema.
Esta capa busca palabras clave exactas. Es "tonta" pero infalible para acciones críticas.

*   **Código:** `_pattern_match` en `intent_classifier.py`
*   **Ejemplo:** Si dices *"sube el volumen"*, detecta "sube" + "volumen" y ejecuta inmediatamente sin pensar.
*   **Ventaja:** Funciona incluso si la IA está caída o la PC está lenta.

### 2. Capa ML (Machine Learning Local)
**Objetivo:** Entender la intención humana sin depender de internet.
Esta es la "magia" local de SARA 2.0. Usa un modelo de embbedings (`all-MiniLM-L6-v2`) para convertir tu texto en números (vectores) y compararlos con ~1000 ejemplos de entrenamiento.

*   **Tecnología:** Sentence-Transformers (HuggingFace).
*   **Funcionamiento:**
    1. Convierte tu comando (ej: *"hay mucho ruido"*) en un vector matemático.
    2. Lo compara matemáticamente (Similitud Coseno) con los vectores de entrenamiento.
    3. Encuentra que *"hay mucho ruido"* se parece matemáticamente a *"baja el volumen"*.
*   **Etiqueta en Chat:** `[ML]`
*   **Ventaja:** Entiende frases que nunca le enseñaste explícitamente, siempre que tengan el mismo significado. No envía datos a la nube (Privacidad).

### 3. Capa IA (Fallback Inteligente)
**Objetivo:** Resolver lo que las capas anteriores no entendieron.
Si la confianza del modelo ML es baja (< 65%), SARA le pregunta a un modelo grande (Gemini/Groq).

*   **Funcionamiento:** Envía un prompt a la IA: *"Clasifica esta frase: [frase usuario] en estas categorías: [lista de intents]"*.
*   **Etiqueta en Chat:** `[AI]`
*   **Ventaja:** Capacidad de razonamiento casi humano. Puede distinguir matices sutiles.

---

## 🛠️ Flujo de Ejecución (`brain.py`)

1. **Limpieza:** Se eliminan "Wake Words" (`Sara`, `Oye Zara`, etc) para limpiar el comando.
2. **Intento Capa 1:** ¿Es un comando crítico? -> EJECUTAR.
3. **Intento Capa 2:** ¿El modelo ML está >65% seguro? -> EJECUTAR.
4. **Intento Capa 3:** Preguntar a la API de IA -> EJECUTAR.
5. **Fallback Final:** Si nada funciona, se trata como una conversación normal ("Charla").

## 📁 Archivos Relacionados
- `intent_classifier.py`: El cerebro que coordina las 3 capas.
- `intent_examples_full.py`: La "escuela" de SARA (1000+ frases de ejemplo para el ML).
- `.sara_models/`: Donde se guardan los modelos neuronales locales para no descargarlos cada vez.

---
**Nota:** Este sistema híbrido hace que SARA sea única: tan rápida como un script, pero tan inteligente como un LLM, sin sacrificar privacidad ni velocidad en el 90% de los casos.
