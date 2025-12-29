# SARA - Changelog

## 🎯 Versión Actual: 3.0.5 (2024-12-28)

### ✨ Nuevas Funcionalidades

#### 📚 Asistente de Estudio
- Resumen de PDFs con IA (Gemini)
- Generación automática de flashcards
- Módulo: `study_assistant.py`

#### 🎮 Control de Videojuegos
- Detección automática de juegos (Steam, Epic, Riot)
- Lanzamiento por voz con búsqueda fuzzy
- Optimización de rendimiento con BAT (3x más rápido)
- Módulo: `game_controller.py`

#### 🏥 Monitor de Salud
- 3 perfiles: Casa, Oficina, Pomodoro
- Recordatorios automáticos de descanso
- Tracking de sesiones de trabajo
- Módulo: `health_monitor.py`

#### 🧹 Limpieza del Sistema
- Limpieza profunda ultra-rápida con scripts BAT
- Elimina: temporales, papelera, cache, prefetch, logs
- Libera memoria RAM
- Scripts: `cleanup_system.bat`, `optimize_gaming.bat`

### ⚡ Optimizaciones
- Scripts BAT nativos para operaciones de sistema (3x más rápido)
- Normalización de acentos en reconocimiento de voz
- Comandos directos sin wake word
- Búsqueda fuzzy para juegos

### 🐛 Correcciones
- Fix: Eco de voz en comandos de volumen
- Fix: Modo Zen no se desactivaba con comandos genéricos
- Fix: Acentos inconsistentes en reconocimiento de voz
- Fix: Prioridad de comandos de salud

### 📦 Dependencias Nuevas
- PyPDF2 (resumen de PDFs)
- fuzzywuzzy (búsqueda de juegos)
- python-Levenshtein (mejora fuzzy search)

---

## 📊 Estadísticas

- **Módulos nuevos:** 3
- **Scripts BAT:** 3
- **Comandos totales:** 37+
- **Mejora de velocidad:** 3x en sistema
- **Líneas de código:** ~1,500 nuevas

---

## 🎯 SARA vs Alexa

| Función | Alexa | SARA |
|---------|-------|------|
| Resumen PDFs | ❌ | ✅ |
| Flashcards | ❌ | ✅ |
| Detectar juegos | ❌ | ✅ |
| Optimizar PC | ❌ | ✅ |
| Monitor salud | ❌ | ✅ |
| Limpieza profunda | ❌ | ✅ |
| Scripts BAT | ❌ | ✅ |

---

## 📖 Documentación

Ver `COMANDOS.md` para la guía completa de comandos.
