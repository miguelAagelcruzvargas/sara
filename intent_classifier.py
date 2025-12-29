"""
🧠 SARA - Hybrid Intent Classifier
===================================

Sistema de clasificación de intenciones en 3 capas:
1. Pattern Matching (0-5ms) - Comandos críticos
2. ML Classifier (50ms) - Sentence-Transformers, 100% offline
3. AI Fallback (1-2s) - Para casos ambiguos

Autor: SARA Team
Fecha: 2025-12-29
"""

import logging
import difflib
import re
import pickle
import hashlib
import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Importar dataset completo
from intent_examples_full import INTENT_EXAMPLES_FULL

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache de embeddings (DENTRO DEL PROYECTO)
PROJECT_DIR = Path(__file__).parent
CACHE_DIR = PROJECT_DIR / ".sara_models"
EMBEDDINGS_CACHE_FILE = CACHE_DIR / "intent_embeddings.pkl"


class HybridIntentClassifier:
    """
    Clasificador híbrido de intenciones que combina pattern matching,
    ML local y AI fallback para máxima robustez y velocidad.
    """
    
    def __init__(self, ia_callback=None):
        """
        Inicializa el clasificador híbrido.
        
        Args:
            ia_callback: Función para consultar IA (opcional, para Layer 3)
        """
        self.ia_callback = ia_callback
        
        # Crear directorio de modelos si no existe
        CACHE_DIR.mkdir(exist_ok=True)
        
        # Configurar cache de Sentence-Transformers DENTRO del proyecto
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(CACHE_DIR)
        
        # Cargar modelo de embeddings (Layer 2)
        logger.info("🧠 Cargando modelo Sentence-Transformers...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=str(CACHE_DIR))
        
        # Cargar ejemplos de entrenamiento
        self.intent_examples = self._cargar_ejemplos()
        
        # Generar embeddings de los ejemplos
        self.intent_embeddings = self._generar_embeddings()
        
        logger.info(f"✅ Intent Classifier inicializado ({len(self.intent_examples)} intenciones)")
        logger.info(f"📁 Modelos guardados en: {CACHE_DIR}")
    
    def _cargar_ejemplos(self) -> Dict[str, list]:
        """
        Carga ejemplos de entrenamiento desde archivo externo.
        Dataset completo con 40+ intenciones y 1000+ ejemplos.
        """
        return INTENT_EXAMPLES_FULL
    
    def _generar_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Genera embeddings para todos los ejemplos de entrenamiento.
        Usa cache en disco para acelerar inicio (3s -> 0.5s).
        """
        # Crear directorio de cache si no existe
        CACHE_DIR.mkdir(exist_ok=True)
        
        # Calcular hash del dataset para detectar cambios
        dataset_str = str(sorted(self.intent_examples.items()))
        dataset_hash = hashlib.md5(dataset_str.encode()).hexdigest()
        
        # Intentar cargar desde cache
        if EMBEDDINGS_CACHE_FILE.exists():
            try:
                with open(EMBEDDINGS_CACHE_FILE, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # Validar que el hash coincida
                if cached_data.get('hash') == dataset_hash:
                    logger.info("✅ Embeddings cargados desde cache (0.5s)")
                    return cached_data['embeddings']
                else:
                    logger.info("⚠️ Cache inválido (dataset cambió), regenerando...")
            except Exception as e:
                logger.warning(f"Error cargando cache: {e}, regenerando...")
        
        # Generar embeddings (primera vez o cache inválido)
        logger.info("🔄 Generando embeddings (esto toma ~3s la primera vez)...")
        embeddings = {}
        for intent, ejemplos in self.intent_examples.items():
            embeddings[intent] = self.model.encode(ejemplos, convert_to_tensor=True)
        
        # Guardar en cache
        try:
            cache_data = {
                'hash': dataset_hash,
                'embeddings': embeddings
            }
            with open(EMBEDDINGS_CACHE_FILE, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info(f"💾 Embeddings guardados en cache: {EMBEDDINGS_CACHE_FILE}")
        except Exception as e:
            logger.warning(f"No se pudo guardar cache: {e}")
        
        return embeddings
    
    def clasificar(self, comando: str) -> Tuple[str, Dict[str, Any], str]:
        """
        Clasifica un comando usando las 3 capas.
        
        Args:
            comando: Comando de voz del usuario
            
        Returns:
            (intent, params, source) donde:
            - intent: Nombre de la intención detectada
            - params: Parámetros extraídos del comando
            - source: "pattern", "ml" o "ai" (capa que lo resolvió)
        """
        cmd = comando.lower().strip()
        
        # CAPA 1: Pattern Matching (comandos críticos)
        intent, params = self._pattern_match(cmd)
        if intent:
            logger.debug(f"✅ Pattern Match: {intent}")
            return intent, params, "pattern"
        
        # CAPA 2: ML Classifier (similitud semántica)
        intent, params, confianza = self._ml_classify(cmd)
        if confianza > 0.65:  # Umbral de confianza
            logger.debug(f"✅ ML Classify: {intent} (confianza: {confianza:.2f})")
            return intent, params, "ml"
        
        # CAPA 3: AI Fallback (casos ambiguos)
        if self.ia_callback and confianza < 0.65:
            intent, params = self._ai_classify(cmd)
            logger.debug(f"✅ AI Fallback: {intent}")
            return intent, params, "ai"
        
        # Fallback final: conversación
        return "CONVERSACION", {"text": comando}, "fallback"
    
    def _pattern_match(self, cmd: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        CAPA 1: Pattern matching para comandos críticos (ultra rápido).
        """
        # Volumen
        if any(x in cmd for x in ["sube", "subir", "súbele", "subele", "más alto", "volumen arriba"]):
            if "volumen" in cmd or "sonido" in cmd or "alto" in cmd:
                return "VOLUMEN_SUBIR", {"amount": 10}
        
        if any(x in cmd for x in ["baja", "bajar", "bájale", "bajale", "más bajo", "volumen abajo"]):
            if "volumen" in cmd or "sonido" in cmd or "bajo" in cmd:
                return "VOLUMEN_BAJAR", {"amount": 10}
        
        if any(x in cmd for x in ["silencio", "mute", "cállate", "silencia"]):
            return "SILENCIO", {}
        
        # Hora/Fecha (muy común)
        if any(x in cmd for x in ["qué hora", "que hora", "hora actual"]):
            return "HORA_FECHA", {"type": "hora"}
        
        if any(x in cmd for x in ["qué día", "que dia", "fecha", "hoy es"]):
            return "HORA_FECHA", {"type": "fecha"}
        
        return None, {}
    
    def _ml_classify(self, cmd: str) -> Tuple[str, Dict[str, Any], float]:
        """
        CAPA 2: Clasificación ML usando similitud semántica.
        """
        # Generar embedding del comando
        cmd_embedding = self.model.encode(cmd, convert_to_tensor=True)
        
        mejor_intent = "CONVERSACION"
        mejor_score = 0.0
        
        # Calcular similitud con cada intención
        for intent, ejemplos_emb in self.intent_embeddings.items():
            similitudes = util.cos_sim(cmd_embedding, ejemplos_emb)
            max_sim = similitudes.max().item()
            
            if max_sim > mejor_score:
                mejor_score = max_sim
                mejor_intent = intent
        
        # Extraer parámetros
        params = self._extraer_parametros(cmd, mejor_intent)
        
        return mejor_intent, params, mejor_score
    
    def _ai_classify(self, cmd: str) -> Tuple[str, Dict[str, Any]]:
        """
        CAPA 3: Clasificación con IA para casos ambiguos.
        """
        if not self.ia_callback:
            return "CONVERSACION", {"text": cmd}
        
        prompt = f"""Clasifica la intención del siguiente comando de voz:

Comando: "{cmd}"

Intenciones posibles:
- MEMORIZAR: Guardar información
- VOLUMEN_SUBIR/VOLUMEN_BAJAR/SILENCIO: Control de audio
- ABRIR_APP: Abrir aplicación
- BUSCAR_WEB: Buscar en internet
- LEER_DOCUMENTO: Leer archivo/página
- REPRODUCIR_MEDIA: Reproducir música/video
- ALARMA: Programar recordatorio
- CLIMA: Consultar clima
- HORA_FECHA: Consultar hora/fecha
- TRADUCIR: Traducir texto
- CALCULAR: Operación matemática
- MODO_ZEN: Activar modo concentración
- CONVERSACION: Charla general

Responde SOLO con JSON:
{{"intent": "NOMBRE_INTENCION", "params": {{"key": "value"}}}}
"""
        
        try:
            respuesta, _ = self.ia_callback(prompt)
            # Limpiar markdown si existe
            if "```" in respuesta:
                respuesta = respuesta.split("```")[1].replace("json", "").strip()
            
            import json
            resultado = json.loads(respuesta)
            return resultado.get("intent", "CONVERSACION"), resultado.get("params", {"text": cmd})
        except Exception as e:
            logger.error(f"Error en AI Classify: {e}")
            return "CONVERSACION", {"text": cmd}
    
    def _extraer_parametros(self, cmd: str, intent: str) -> Dict[str, Any]:
        """
        Extrae parámetros del comando según la intención.
        """
        params = {}
        
        if intent == "MEMORIZAR":
            # Remover triggers comunes
            dato = cmd
            for trigger in ["memoriza", "memorizar", "guarda", "guardar", "recuerda", "recordar", "anota", "anotar", "que", "esto", ":", "sara"]:
                dato = dato.replace(trigger, "")
            params["data"] = dato.strip()
        
        elif intent == "ABRIR_APP":
            # Extraer nombre de app
            app_name = cmd.replace("abre", "").replace("abrir", "").replace("lanza", "").replace("ejecuta", "").strip()
            params["app_name"] = app_name
        
        elif intent == "BUSCAR_WEB":
            # Extraer query
            query = cmd
            for trigger in ["busca", "buscar", "investiga", "investigar", "googlea", "en google", "sobre"]:
                query = query.replace(trigger, "")
            params["query"] = query.strip()
        
        elif intent == "REPRODUCIR_MEDIA":
            # Extraer query
            query = cmd.replace("pon", "").replace("reproduce", "").replace("música", "").replace("en youtube", "").strip()
            params["query"] = query
        
        elif intent == "ALARMA":
            # Extraer tiempo (simplificado, puede mejorarse)
            match = re.search(r'(\d+)\s*(minuto|hora)', cmd)
            if match:
                cantidad = int(match.group(1))
                unidad = match.group(2)
                params["minutes"] = cantidad if unidad == "minuto" else cantidad * 60
                params["message"] = "Alarma"
        
        elif intent == "TRADUCIR":
            # Extraer texto e idioma
            if "al inglés" in cmd or "al ingles" in cmd:
                params["target_lang"] = "en"
            elif "al español" in cmd:
                params["target_lang"] = "es"
            
            texto = cmd.replace("traduce", "").replace("al inglés", "").replace("al español", "").strip()
            params["text"] = texto
        
        elif intent == "CALCULAR":
            # Extraer expresión matemática
            expr = cmd.replace("cuánto es", "").replace("calcula", "").replace("divide", "/").replace("por", "*").replace("más", "+").replace("menos", "-").replace("entre", "/").strip()
            params["expression"] = expr
        
        else:
            params["text"] = cmd
        
        return params


# Función de utilidad para testing
if __name__ == "__main__":
    # Test básico
    classifier = HybridIntentClassifier()
    
    test_commands = [
        "sube el volumen",
        "memoriza que la clave es 777",
        "abre chrome",
        "busca recetas de pasta",
        "qué hora es",
        "pon música lofi",
    ]
    
    print("\n🧪 TESTING INTENT CLASSIFIER\n" + "="*50)
    for cmd in test_commands:
        intent, params, source = classifier.clasificar(cmd)
        print(f"\n📝 Comando: '{cmd}'")
        print(f"   Intent: {intent}")
        print(f"   Params: {params}")
        print(f"   Source: {source}")
