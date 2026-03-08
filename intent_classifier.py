"""
🧠 SARA - Hybrid Intent Classifier (FINAL PRODUCTION VERSION)
=============================================================

Sistema de clasificación de intenciones en 3 capas:
1. Pattern Matching (0-5ms) - Comandos críticos (Con protección de negación)
2. ML Classifier (50ms) - Sentence-Transformers (Extracción segura)
3. AI Fallback (1-2s) - Contexto dinámico inteligente

Autor: SARA Team
Fecha: 2025-12-29
"""

import logging
import re
import pickle
import hashlib
import os
import time
import json 
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import numpy as np

# Dependencia externa principal
from sentence_transformers import SentenceTransformer, util

# Importar dataset completo (Asegúrate de que este archivo tenga el dict completo)
from intent_examples_full import INTENT_EXAMPLES_FULL

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas y Cache
PROJECT_DIR = Path(__file__).parent
CACHE_DIR = PROJECT_DIR / ".sara_models"
EMBEDDINGS_CACHE_FILE = CACHE_DIR / "intent_embeddings.pkl"
COMMAND_CACHE_FILE = CACHE_DIR / "command_cache.pkl"


class HybridIntentClassifier:
    """
    Clasificador híbrido optimizado para producción.
    """
    
    def __init__(self, ia_callback=None, splash_callback=None):
        self.ia_callback = ia_callback
        self.splash_callback = splash_callback
        
        # Crear directorio de modelos
        CACHE_DIR.mkdir(exist_ok=True)
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(CACHE_DIR)
        
        # Caché de comandos recientes
        self.command_cache = {} 
        self.cache_max_size = 50
        self.cache_ttl = 300 
        
        # Cargar caché persistente
        self._cargar_cache_comandos()
        
        # Cargar modelo ML (Layer 2)
        if self.splash_callback:
            self.splash_callback(30, "Cargando modelo NLU...", "Sentence-Transformers")
        
        logger.info("🧠 Cargando modelo Sentence-Transformers...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', cache_folder=str(CACHE_DIR))
        
        # Cargar datos
        if self.splash_callback:
            self.splash_callback(50, "Cargando ejemplos...", "Dataset completo")
        
        self.intent_examples = INTENT_EXAMPLES_FULL
        
        # Generar embeddings
        if self.splash_callback:
            self.splash_callback(60, "Generando embeddings...", "Calculando vectores")
        
        self.intent_embeddings = self._generar_embeddings()
        
        if self.splash_callback:
            self.splash_callback(80, "NLU listo", f"{len(self.intent_examples)} intenciones")
        
        logger.info(f"✅ Intent Classifier inicializado ({len(self.intent_examples)} intenciones)")

    def _generar_embeddings(self) -> Dict[str, np.ndarray]:
        """Genera o carga embeddings validando hash."""
        dataset_str = str(sorted(self.intent_examples.items()))
        dataset_hash = hashlib.md5(dataset_str.encode()).hexdigest()
        
        if EMBEDDINGS_CACHE_FILE.exists():
            try:
                with open(EMBEDDINGS_CACHE_FILE, 'rb') as f:
                    cached_data = pickle.load(f)
                if cached_data.get('hash') == dataset_hash:
                    logger.info("✅ Embeddings cargados desde cache")
                    return cached_data['embeddings']
            except Exception as e:
                logger.warning(f"Cache inválido o corrupto: {e}")
        
        logger.info("🔄 Generando embeddings frescos...")
        embeddings = {}
        for intent, ejemplos in self.intent_examples.items():
            embeddings[intent] = self.model.encode(ejemplos, convert_to_tensor=True)
        
        try:
            with open(EMBEDDINGS_CACHE_FILE, 'wb') as f:
                pickle.dump({'hash': dataset_hash, 'embeddings': embeddings}, f)
        except Exception as e:
            logger.warning(f"No se pudo guardar cache: {e}")
        
        return embeddings
    
    def clasificar(self, comando: str) -> Tuple[str, Dict[str, Any], str]:
        """Clasifica comandos usando lógica de 3 capas robusta."""
        cmd = comando.lower().strip()
        
        # Limpieza de Wake Words
        wake_words_pattern = r"^(sara|zara|oye sara|hola sara|ok sara)\b[\s,.]*"
        cmd = re.sub(wake_words_pattern, "", cmd, count=1).strip()
        
        if not cmd:
            return "CONVERSACION", {"text": comando}, "empty"
        
        # 1. Caché (Optimización 0ms)
        cmd_normalizado = self._normalizar_comando(cmd)
        if cmd_normalizado in self.command_cache:
            res = self.command_cache[cmd_normalizado]
            if time.time() - res[3] < self.cache_ttl:
                return res[0], res[1], "cache"
        
        # 2. Pattern Matching (Con protección de negación)
        intent, params = self._pattern_match(cmd)
        if intent:
            self._guardar_en_cache(cmd_normalizado, intent, params, "pattern")
            return intent, params, "pattern"
        
        # 3. ML Classifier
        intent, params, confianza = self._ml_classify(cmd)
        
        # Bloqueo de Alucinaciones / Basura
        if intent == "OUT_OF_SCOPE" and confianza > 0.55:
            return "CONVERSACION", {"text": cmd, "ignored": True}, "ml_garbage"

        # Umbral ML ajustado (sin huecos)
        if confianza > 0.60:
            self._guardar_en_cache(cmd_normalizado, intent, params, "ml")
            return intent, params, "ml"
        
        # 4. AI Fallback (Si hay callback)
        if self.ia_callback and confianza > 0.35:
            intent_ai, params_ai = self._ai_classify(cmd)
            # Solo guardamos en caché si la IA devolvió una intención válida
            if intent_ai != "CONVERSACION":
                self._guardar_en_cache(cmd_normalizado, intent_ai, params_ai, "ai")
            return intent_ai, params_ai, "ai"
        
        # 5. Fallback final
        return "CONVERSACION", {
            "text": comando, 
            "suggestions": self._generar_sugerencias(cmd, confianza)
        }, "fallback"
    
    def _pattern_match(self, cmd: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Capa 1: ESTRICTA. Si hay negación, aborta para que decida el ML.
        """
        # Guardia de Negación ESTRICTA
        negation_trigger = re.search(r'\b(no|cancelar|detener|espera|alto)\b', cmd)
        if negation_trigger:
            # Ante cualquier duda o negación, pasamos al ML (Capa 2) que entiende contexto
            return None, {}

        # Volumen
        if any(x in cmd for x in ["sube", "subir", "súbele", "más alto", "volumen arriba"]):
            if "volumen" in cmd or "sonido" in cmd or "alto" in cmd:
                return "VOLUMEN_SUBIR", {"amount": 10}
        
        if any(x in cmd for x in ["baja", "bajar", "bájale", "más bajo", "volumen abajo"]):
            if "volumen" in cmd or "sonido" in cmd or "bajo" in cmd:
                return "VOLUMEN_BAJAR", {"amount": 10}
        
        if any(x in cmd for x in ["silencio", "mute", "cállate", "silencia"]):
            return "SILENCIO", {}
        
        # Hora/Fecha
        if "hora" in cmd and ("que" in cmd or "dime" in cmd):
            return "HORA_FECHA", {"type": "hora"}
            
        # Apps (Regex simple)
        if re.search(r'\b(abre|abrir|lanza|ejecuta)\b', cmd):
            app_name = re.sub(r'\b(abre|abrir|lanza|ejecuta)\b', '', cmd).strip()
            if app_name: return "ABRIR_APP", {"app_name": app_name}

        # Media Control
        if any(x in cmd for x in ["pausa", "detener música"]): return "REPRODUCIR_MEDIA", {"action": "pause"}
        if any(x in cmd for x in ["reproduce", "continua", "play"]): return "REPRODUCIR_MEDIA", {"action": "play"}

        # Sentinel / Seguridad - VARIANTES AMPLIADAS
        # Activación
        if any(x in cmd for x in [
            "activar sentinela", "activa sentinela", "activar modo sentinela", 
            "activar modo guardia", "activa modo guardia", "modo centinela",
            "modo sentinela", "sentinel", "centinela", "sentinel on",
            "protege el sistema", "bloquea el sistema", "bloquea pantalla",
            "bloquea la pantalla", "bloquea acceso", "bloquea el acceso",
            "activar seguridad", "activa seguridad", "modo seguridad",
            "pon modo sentinela", "pon modo centinela", "ponte en guardia",
            "activar vigilancia", "activa vigilancia", "inicia sentinel"
        ]):
            return "SENTINEL_ACTIVAR", {}
        
        # Desactivación
        if any(x in cmd for x in [
            "desactivar sentinela", "desactiva sentinela", "desactivar modo sentinela",
            "desactivar modo guardia", "desactiva modo guardia", "quita modo guardia",
            "quita el modo guardia", "apagar centinela", "apaga centinela",
            "apagar sentinela", "apaga sentinela", "sentinel off",
            "desbloquea el sistema", "desbloquea sistema", "desbloquea pantalla",
            "desbloquea la pantalla", "desbloquea acceso", "desbloquea el acceso",
            "desactivar seguridad", "desactiva seguridad", "quita seguridad",
            "ya llegué", "descansar centinela", "descansa centinela",
            "terminar vigilancia", "termina vigilancia", "falsa alarma",
            "cancelar sentinel", "cancela sentinel", "salir modo sentinela"
        ]):
            return "SENTINEL_DESACTIVAR", {}

        # UI / Configuración
        if any(x in cmd for x in ["abre configuración", "abrir configuración", "ajustes", "configuracion", "settings"]):
            return "CONFIGURACION", {}
        if any(x in cmd for x in ["mi perfil", "ver perfil", "mostrar perfil"]):
            return "PERFIL", {}
        
        return None, {}
    
    def _ml_classify(self, cmd: str) -> Tuple[str, Dict[str, Any], float]:
        """Capa 2: Similitud semántica vectorial."""
        cmd_embedding = self.model.encode(cmd, convert_to_tensor=True)
        
        mejor_intent = "CONVERSACION"
        mejor_score = 0.0
        
        for intent, ejemplos_emb in self.intent_embeddings.items():
            similitudes = util.cos_sim(cmd_embedding, ejemplos_emb)
            max_sim = similitudes.max().item()
            
            if max_sim > mejor_score:
                mejor_score = max_sim
                mejor_intent = intent
        
        params = self._extraer_parametros(cmd, mejor_intent)
        return mejor_intent, params, mejor_score
    
    def _ai_classify(self, cmd: str) -> Tuple[str, Dict[str, Any]]:
        """
        Capa 3: Filtrado dinámico Top-5 y manejo robusto de JSON.
        """
        if not self.ia_callback:
            return "CONVERSACION", {"text": cmd}

        # Selección dinámica de candidatos (Top 5 ML)
        scores_candidatos = []
        cmd_embedding = self.model.encode(cmd, convert_to_tensor=True)
        
        for intent, ejemplos_emb in self.intent_embeddings.items():
            if intent in ["CONVERSACION", "OUT_OF_SCOPE"]: continue
            similitudes = util.cos_sim(cmd_embedding, ejemplos_emb)
            max_sim = similitudes.max().item()
            scores_candidatos.append((max_sim, intent))
        
        scores_candidatos.sort(reverse=True, key=lambda x: x[0])
        top_intents = [x[1] for x in scores_candidatos[:5]]
        
        ejemplos_contexto = []
        for intent in top_intents:
            ejs = ", ".join(self.intent_examples[intent][:3])
            ejemplos_contexto.append(f"- {intent}: {ejs}")
        
        contexto_str = "\n".join(ejemplos_contexto)

        prompt = f"""Clasifica este comando ambiguo.
Comando: "{cmd}"

Opciones probables (Top 5 ML):
{contexto_str}

Si no encaja, responde CONVERSACION.
Devuelve JSON: {{"intent": "X", "params": {{...}}}}"""
        
        try:
            respuesta, _ = self.ia_callback(prompt)
            
            # Limpieza y parseo robusto de JSON
            start = respuesta.find('{')
            end = respuesta.rfind('}') + 1
            
            if start != -1 and end != -1:
                json_str = respuesta[start:end]
                # Limpiar saltos de línea y errores comunes
                json_str = re.sub(r'[\n\r\t]', ' ', json_str)
                json_str = re.sub(r',\s*}', '}', json_str)
                
                resultado = json.loads(json_str)
                intent = resultado.get("intent", "CONVERSACION")
                
                if intent not in self.intent_examples: 
                    intent = "CONVERSACION"
                    
                params = resultado.get("params", {"text": cmd})
                return intent, params
            else:
                return "CONVERSACION", {"text": cmd}

        except Exception as e:
            logger.warning(f"AI Fallback falló (JSON inválido o error): {e}")
            return "CONVERSACION", {"text": cmd}

    def _extraer_parametros(self, cmd: str, intent: str) -> Dict[str, Any]:
        """
        Extracción de parámetros segura usando Regex (Boundaries \b).
        """
        params = {}
        
        def clean_triggers(text, triggers):
            for t in triggers:
                # \b evita que "busca" rompa "buscador"
                text = re.sub(r'\b' + re.escape(t) + r'\b', '', text, flags=re.IGNORECASE)
            return text.strip()

        if intent == "MEMORIZAR":
            triggers = ["memoriza", "guarda", "recuerda", "anota", "que", "esto", "sara"]
            params["data"] = clean_triggers(cmd, triggers)
            
        elif intent == "BUSCAR_WEB":
            triggers = ["busca", "investiga", "googlea", "guglea", "en google", "sobre", "informacion", "de"]
            params["query"] = clean_triggers(cmd, triggers)
            
        elif intent == "ABRIR_APP":
            triggers = ["abre", "abrir", "lanza", "ejecuta", "inicia", "app"]
            params["app_name"] = clean_triggers(cmd, triggers)
            
        elif intent == "ALARMA":
            nums = [int(s) for s in re.findall(r'\d+', cmd)]
            if nums:
                mult = 60 if re.search(r'\b(hora|horas)\b', cmd) else 1
                params["minutes"] = nums[0] * mult
            else:
                params["minutes"] = 5
                
        elif intent == "CALCULAR":
            expr = cmd
            replacements = [
                ("cuanto es", ""), ("calcula", ""), ("dime", ""), 
                ("por", "*"), ("entre", "/"), ("mas", "+"), ("menos", "-")
            ]
            for old, new in replacements:
                expr = re.sub(r'\b' + re.escape(old) + r'\b', new, expr)
            params["expression"] = expr.strip()
            
        elif intent in ["GIT_PUSH", "GIT_PULL", "GIT_STATUS"]:
             pass
             
        elif intent == "TRADUCIR":
            if re.search(r'ingles|inglés', cmd): params["target_lang"] = "en"
            elif re.search(r'frances|francés', cmd): params["target_lang"] = "fr"
            else: params["target_lang"] = "es"
            
            triggers = ["traduce", "al ingles", "al español", "texto", "dime"]
            params["text"] = clean_triggers(cmd, triggers)

        else:
            params["text"] = cmd
            
        return params

    # Métodos auxiliares
    def _normalizar_comando(self, cmd: str) -> str:
        cmd = re.sub(r'[^\w\s]', '', cmd.lower())
        return re.sub(r'\s+', ' ', cmd).strip()
    
    def _guardar_en_cache(self, cmd_normalizado: str, intent: str, params: Dict, source: str):
        if len(self.command_cache) >= self.cache_max_size:
            keys_sorted = sorted(self.command_cache.keys(), key=lambda k: self.command_cache[k][3])
            for k in keys_sorted[:10]:
                del self.command_cache[k]
        
        self.command_cache[cmd_normalizado] = (intent, params, source, time.time())
        self._guardar_cache_persistente()
    
    def _cargar_cache_comandos(self):
        if COMMAND_CACHE_FILE.exists():
            try:
                with open(COMMAND_CACHE_FILE, 'rb') as f:
                    data = pickle.load(f)
                    now = time.time()
                    self.command_cache = {k:v for k,v in data.items() if now - v[3] < self.cache_ttl}
            except: self.command_cache = {}
            
    def _guardar_cache_persistente(self):
        if not hasattr(self, '_save_count'): self._save_count = 0
        self._save_count += 1
        if self._save_count >= 5:
            try:
                with open(COMMAND_CACHE_FILE, 'wb') as f:
                    pickle.dump(self.command_cache, f)
                self._save_count = 0
            except: pass

    def _generar_sugerencias(self, cmd: str, confianza: float) -> List[str]:
        if confianza < 0.3:
            return ["No entendí bien, ¿puedes repetir?"]
        return []

# Testing block
if __name__ == "__main__":
    classifier = HybridIntentClassifier()
    print("✅ Sistema listo para integración")