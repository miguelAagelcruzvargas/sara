"""
Code Reviewer - Sistema de revisión de código con IA
Analiza archivos Python y genera sugerencias de mejora
"""

import os
import logging
from typing import Callable, Optional, Dict, List, Tuple

class CodeReviewer:
    """Revisor de código con IA para análisis y sugerencias."""
    
    def __init__(self, ia_callback: Optional[Callable] = None):
        """
        Inicializa el revisor de código.
        
        Args:
            ia_callback: Función para consultar la IA (debe devolver tupla (texto, tipo))
        """
        self.ia_callback = ia_callback
        logging.info("✅ CodeReviewer inicializado")
    
    def analizar_archivo(self, ruta_archivo: str, tipo_analisis: str = "quick") -> Tuple[str, str]:
        """
        Analiza un archivo Python.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            tipo_analisis: 'quick', 'deep', 'security', 'performance'
        
        Returns:
            Tupla (resultado, tipo)
        """
        if not self.ia_callback:
            return "❌ IA no disponible para Code Review", "error"
        
        # Verificar que el archivo existe
        if not os.path.exists(ruta_archivo):
            return f"❌ Archivo no encontrado: {ruta_archivo}", "error"
        
        # Verificar que es un archivo Python
        if not ruta_archivo.endswith('.py'):
            return "❌ Solo se pueden analizar archivos Python (.py)", "error"
        
        # Leer el archivo
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
        except Exception as e:
            return f"❌ Error leyendo archivo: {e}", "error"
        
        # Limitar tamaño del código (máximo 3000 líneas)
        lineas = codigo.split('\n')
        if len(lineas) > 3000:
            return f"❌ Archivo muy grande ({len(lineas)} líneas). Máximo: 3000 líneas", "error"
        
        # Generar prompt según tipo de análisis
        prompt = self._generar_prompt_analisis(codigo, ruta_archivo, tipo_analisis)
        
        # Consultar IA
        try:
            resultado, tipo = self.ia_callback(prompt)
            return resultado, "ai"
        except Exception as e:
            logging.error(f"Error en análisis de código: {e}")
            return f"❌ Error en análisis: {e}", "error"
    
    def _generar_prompt_analisis(self, codigo: str, ruta: str, tipo: str) -> str:
        """Genera el prompt para la IA según el tipo de análisis."""
        
        nombre_archivo = os.path.basename(ruta)
        
        prompts = {
            "quick": f"""Analiza este código Python y proporciona un resumen breve:

Archivo: {nombre_archivo}

```python
{codigo}
```

Proporciona:
1. Resumen general (2-3 líneas)
2. 3-5 problemas principales encontrados
3. 3 sugerencias de mejora prioritarias

Sé conciso y directo.""",

            "deep": f"""Realiza un análisis profundo de este código Python:

Archivo: {nombre_archivo}

```python
{codigo}
```

Analiza:
1. **Estructura y Organización**: Calidad del diseño
2. **Code Smells**: Duplicación, complejidad, nombres poco claros
3. **Buenas Prácticas**: PEP 8, docstrings, type hints
4. **Lógica**: Posibles bugs, edge cases no manejados
5. **Rendimiento**: Optimizaciones posibles
6. **Mantenibilidad**: Facilidad de modificar/extender

Proporciona ejemplos concretos con números de línea cuando sea posible.""",

            "security": f"""Analiza la seguridad de este código Python:

Archivo: {nombre_archivo}

```python
{codigo}
```

Busca:
1. **Vulnerabilidades**: Inyección, XSS, path traversal
2. **Manejo de datos sensibles**: Passwords, API keys hardcodeadas
3. **Validación de entrada**: Input sin sanitizar
4. **Dependencias**: Imports peligrosos
5. **Permisos**: Operaciones de archivos/sistema

Clasifica por severidad: CRÍTICO, ALTO, MEDIO, BAJO.""",

            "performance": f"""Analiza el rendimiento de este código Python:

Archivo: {nombre_archivo}

```python
{codigo}
```

Identifica:
1. **Cuellos de botella**: Loops ineficientes, operaciones costosas
2. **Uso de memoria**: Estructuras de datos inadecuadas
3. **I/O**: Operaciones bloqueantes, falta de caché
4. **Algoritmos**: Complejidad O(n²) o peor
5. **Optimizaciones**: Sugerencias concretas con código

Prioriza las mejoras por impacto."""
        }
        
        return prompts.get(tipo, prompts["quick"])
    
    def generar_tests(self, ruta_archivo: str) -> Tuple[str, str]:
        """
        Genera tests unitarios para un archivo Python.
        
        Args:
            ruta_archivo: Ruta al archivo
        
        Returns:
            Tupla (código de tests, tipo)
        """
        if not self.ia_callback:
            return "❌ IA no disponible", "error"
        
        if not os.path.exists(ruta_archivo):
            return f"❌ Archivo no encontrado: {ruta_archivo}", "error"
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
        except Exception as e:
            return f"❌ Error leyendo archivo: {e}", "error"
        
        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_test = f"test_{nombre_archivo}"
        
        prompt = f"""Genera tests unitarios con pytest para este código Python:

Archivo: {nombre_archivo}

```python
{codigo}
```

Genera un archivo de tests completo ({nombre_test}) que incluya:
1. Imports necesarios (pytest, el módulo a testear)
2. Fixtures si son necesarias
3. Tests para cada función/método público
4. Tests de casos edge
5. Tests de manejo de errores

El código debe ser ejecutable directamente. Usa asserts claros y nombres descriptivos."""

        try:
            resultado, _ = self.ia_callback(prompt)
            return resultado, "ai"
        except Exception as e:
            return f"❌ Error generando tests: {e}", "error"
    
    def generar_documentacion(self, ruta_archivo: str) -> Tuple[str, str]:
        """
        Genera/mejora docstrings para un archivo Python.
        
        Args:
            ruta_archivo: Ruta al archivo
        
        Returns:
            Tupla (código con docstrings, tipo)
        """
        if not self.ia_callback:
            return "❌ IA no disponible", "error"
        
        if not os.path.exists(ruta_archivo):
            return f"❌ Archivo no encontrado: {ruta_archivo}", "error"
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
        except Exception as e:
            return f"❌ Error leyendo archivo: {e}", "error"
        
        nombre_archivo = os.path.basename(ruta_archivo)
        
        prompt = f"""Mejora la documentación de este código Python:

Archivo: {nombre_archivo}

```python
{codigo}
```

Genera el código COMPLETO con:
1. Docstring de módulo al inicio (descripción, autor, fecha)
2. Docstrings de Google style para cada clase
3. Docstrings para cada método/función (Args, Returns, Raises)
4. Type hints donde falten
5. Comentarios inline para lógica compleja

Devuelve el código completo mejorado, no solo las docstrings."""

        try:
            resultado, _ = self.ia_callback(prompt)
            return resultado, "ai"
        except Exception as e:
            return f"❌ Error generando documentación: {e}", "error"
    
    def sugerir_refactoring(self, ruta_archivo: str) -> Tuple[str, str]:
        """
        Sugiere refactorizaciones para mejorar el código.
        
        Args:
            ruta_archivo: Ruta al archivo
        
        Returns:
            Tupla (sugerencias, tipo)
        """
        if not self.ia_callback:
            return "❌ IA no disponible", "error"
        
        if not os.path.exists(ruta_archivo):
            return f"❌ Archivo no encontrado: {ruta_archivo}", "error"
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
        except Exception as e:
            return f"❌ Error leyendo archivo: {e}", "error"
        
        nombre_archivo = os.path.basename(ruta_archivo)
        
        prompt = f"""Sugiere refactorizaciones para este código Python:

Archivo: {nombre_archivo}

```python
{codigo}
```

Identifica oportunidades de refactoring:
1. **Extraer funciones**: Bloques de código repetidos o complejos
2. **Simplificar condicionales**: If/else anidados
3. **Mejorar nombres**: Variables/funciones poco claras
4. **Aplicar patrones**: Design patterns aplicables
5. **Reducir acoplamiento**: Dependencias innecesarias

Para cada sugerencia:
- Explica el problema
- Muestra código ANTES
- Muestra código DESPUÉS mejorado
- Justifica el beneficio"""

        try:
            resultado, _ = self.ia_callback(prompt)
            return resultado, "ai"
        except Exception as e:
            return f"❌ Error sugiriendo refactoring: {e}", "error"
    
    def explicar_codigo(self, ruta_archivo: str) -> Tuple[str, str]:
        """
        Genera una explicación detallada del código.
        
        Args:
            ruta_archivo: Ruta al archivo
        
        Returns:
            Tupla (explicación, tipo)
        """
        if not self.ia_callback:
            return "❌ IA no disponible", "error"
        
        if not os.path.exists(ruta_archivo):
            return f"❌ Archivo no encontrado: {ruta_archivo}", "error"
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
        except Exception as e:
            return f"❌ Error leyendo archivo: {e}", "error"
        
        nombre_archivo = os.path.basename(ruta_archivo)
        
        prompt = f"""Explica este código Python de forma clara y didáctica:

Archivo: {nombre_archivo}

```python
{codigo}
```

Proporciona:
1. **Propósito general**: Qué hace este archivo
2. **Estructura**: Clases, funciones principales
3. **Flujo**: Cómo funciona paso a paso
4. **Dependencias**: Qué importa y por qué
5. **Casos de uso**: Ejemplos de cómo usarlo

Usa lenguaje simple, como si explicaras a un colega."""

        try:
            resultado, _ = self.ia_callback(prompt)
            return resultado, "ai"
        except Exception as e:
            return f"❌ Error explicando código: {e}", "error"


# Singleton para acceso global
_reviewer_instance = None

def obtener_reviewer(ia_callback: Optional[Callable] = None) -> CodeReviewer:
    """
    Obtiene la instancia singleton de CodeReviewer.
    
    Args:
        ia_callback: Función para consultar la IA
    
    Returns:
        Instancia de CodeReviewer
    """
    global _reviewer_instance
    if _reviewer_instance is None:
        _reviewer_instance = CodeReviewer(ia_callback)
    return _reviewer_instance
