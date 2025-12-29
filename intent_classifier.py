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
from typing import Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        
        # Cargar modelo de embeddings (Layer 2)
        logger.info("🧠 Cargando modelo Sentence-Transformers...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cargar ejemplos de entrenamiento
        self.intent_examples = self._cargar_ejemplos()
        
        # Generar embeddings de los ejemplos
        self.intent_embeddings = self._generar_embeddings()
        
        logger.info(f"✅ Intent Classifier inicializado ({len(self.intent_examples)} intenciones)")
    
    def _cargar_ejemplos(self) -> Dict[str, list]:
        """
        Define ejemplos de entrenamiento para cada intención.
        Incluye variaciones naturales, modismos mexicanos y errores comunes de reconocimiento de voz.
        """
        return {
            "MEMORIZAR": [
                # Variaciones estándar
                "memoriza que la clave es 777",
                "guarda esto: dato importante",
                "recuerda que mañana tengo cita",
                "anota el código ABC123",
                "no olvides que el wifi es password123",
                "apunta que debo llamar a Juan",
                "registra que el proyecto se entrega el viernes",
                "toma nota de que María llamó",
                "anota mi número de cuenta 12345",
                "guarda mi dirección calle 123",
                # Modismos mexicanos
                "apúntale que tengo junta a las 3",
                "no se te olvide que debo pagar la luz",
                "acuérdate que hoy es cumpleaños de mi mamá",
                "anótale que necesito comprar leche",
                # Errores comunes de reconocimiento
                "memoriza qué la clave es 777",  # "qué" en vez de "que"
                "memoriza está clave es 777",    # "está" en vez de "que"
                "guarda está información",
                "memoriza qué tengo cita",
                # Sin artículos
                "memoriza clave es 777",
                "guarda dato importante",
                "anota código ABC",
                # Variaciones de verbo
                "almacena que la reunión es mañana",
                "graba que el password es 123",
                "registra mi cumpleaños es el 15",
            ],
            
            "VOLUMEN_SUBIR": [
                # Variaciones estándar
                "sube el volumen",
                "súbele volumen",
                "más alto",
                "aumenta el sonido",
                "volumen arriba",
                "subir volumen",
                "sube volumen",
                # Modismos mexicanos
                "súbele",
                "ponle más recio",
                "échale más volumen",
                "métele más",
                "dale más duro",
                "ponlo más fuerte",
                # Sin artículos
                "sube volumen",
                "subir sonido",
                # Errores de reconocimiento
                "subele volumen",  # sin tilde
                "sube el volumen",
                # Variaciones naturales
                "no te escucho sube",
                "volumen al máximo",
                "ponlo al 100",
                "aumenta audio",
                "más duro",
                "más fuerte",
                "volumen alto",
            ],
            
            "VOLUMEN_BAJAR": [
                # Variaciones estándar
                "baja el volumen",
                "bájale volumen",
                "más bajo",
                "disminuye el sonido",
                "volumen abajo",
                "bajar volumen",
                "baja volumen",
                # Modismos mexicanos
                "bájale",
                "ponle más bajito",
                "échale menos volumen",
                "quítale volumen",
                "bájale tantito",
                # Sin artículos
                "baja volumen",
                "bajar sonido",
                # Errores de reconocimiento
                "bajale volumen",  # sin tilde
                "baja el volumen",
                # Variaciones naturales
                "está muy alto baja",
                "volumen al mínimo",
                "ponlo bajito",
                "disminuye audio",
                "menos fuerte",
                "más suave",
            ],
            
            "SILENCIO": [
                "silencio",
                "mute",
                "cállate",
                "silencia",
                "mutea",
                "quita el sonido",
                "sin sonido",
                "apaga el audio",
                "quita audio",
                "calla",
                "shh",
                "silencio total",
                "mutear",
                "pon mute",
            ],
            
            "ABRIR_APP": [
                # Navegadores
                "abre chrome",
                "abrir chrome",
                "abre google chrome",
                "abre firefox",
                "abre edge",
                # Editores
                "abre visual studio code",
                "abrir vscode",
                "abre vs code",
                "abre notepad",
                "abre bloc de notas",
                "abre word",
                "abre excel",
                # Comunicación
                "abre discord",
                "abrir discord",
                "abre whatsapp",
                "abre telegram",
                "abre slack",
                # Multimedia
                "abre spotify",
                "abrir spotify",
                "abre vlc",
                # Variaciones de verbo
                "lanza chrome",
                "ejecuta notepad",
                "inicia discord",
                "arranca spotify",
                # Sin artículos
                "abre chrome",
                "abrir word",
            ],
            
            "BUSCAR_WEB": [
                # Con "busca"
                "busca en google inteligencia artificial",
                "busca python",
                "busca recetas de pasta",
                "busca noticias de tecnología",
                "busca cómo hacer pan",
                # Con "investiga"
                "investiga sobre machine learning",
                "investiga sobre python",
                "investiga inteligencia artificial",
                # Con "googlea"
                "googlea recetas de pasta",
                "googlea noticias",
                "googlea python tutorial",
                # Preguntas directas
                "qué es machine learning",
                "qué es python",
                "cómo funciona la IA",
                "cuál es la capital de Francia",
                # Con "búscame"
                "búscame información de tensorflow",
                "búscame tutoriales de python",
                "búscame recetas mexicanas",
                # Modismos
                "échame una búsqueda de python",
                "investígame sobre IA",
                # Sin preposiciones
                "busca inteligencia artificial",
                "investiga python",
            ],
            
            "LEER_DOCUMENTO": [
                "lee este archivo",
                "lee este documento",
                "qué dice esta página",
                "que dice esta página",  # sin tilde
                "lee esta web",
                "que dice este pdf",
                "lee este pdf",
                "abre este documento",
                "lee el archivo",
                "qué dice el documento",
                "lee la página",
                "muéstrame este archivo",
                "dime qué dice",
                "lee esto",
                "qué contiene este archivo",
            ],
            
            "REPRODUCIR_MEDIA": [
                # Con "pon"
                "pon música",
                "pon rock",
                "pon lofi",
                "pon una canción",
                "pon reggaeton",
                # Con "reproduce"
                "reproduce rock",
                "reproduce en youtube",
                "reproduce música",
                "reproduce lofi",
                # Con "ponle"
                "ponle música",
                "ponle rock",
                "ponle lofi",
                # Específico
                "pon música relajante",
                "reproduce música para estudiar",
                "pon algo de rock",
                "ponme música",
                # Modismos
                "échale música",
                "métele rock",
                "dale play a lofi",
            ],
            
            "ALARMA": [
                # En minutos
                "alarma en 5 minutos",
                "alarma en 10 minutos",
                "alarma en 30 minutos",
                "pon alarma en 5 minutos",
                "pon una alarma en 10 minutos",
                # Recuérdame
                "recuérdame en 5 minutos",
                "recuérdame en 10 minutos",
                "recuérdame en media hora",
                # Timer
                "pon un timer de 5 minutos",
                "timer de 10 minutos",
                "temporizador de 30 minutos",
                # Avísame
                "avísame en 5 minutos",
                "avísame en una hora",
                "avísame en 10",
                # Variaciones
                "programa alarma 5 minutos",
                "configura timer 10 minutos",
            ],
            
            "CLIMA": [
                "qué clima hace",
                "que clima hace",  # sin tilde
                "cómo está el clima",
                "como está el clima",  # sin tilde
                "temperatura actual",
                "cuál es la temperatura",
                "va a llover hoy",
                "va a llover",
                "qué tiempo hace",
                "cómo está el tiempo",
                "clima de hoy",
                "pronóstico del tiempo",
                "hace frío",
                "hace calor",
                "temperatura",
            ],
            
            "HORA_FECHA": [
                # Hora
                "qué hora es",
                "que hora es",  # sin tilde
                "hora actual",
                "dime la hora",
                "cuál es la hora",
                "qué horas son",
                # Fecha
                "qué día es hoy",
                "que día es hoy",  # sin tilde
                "fecha de hoy",
                "cuál es la fecha",
                "qué fecha es",
                "día de hoy",
                "en qué fecha estamos",
                "a cuántos estamos",
            ],
            
            "TRADUCIR": [
                # Al inglés
                "traduce esto al inglés",
                "traduce al inglés hola",
                "cómo se dice hola en inglés",
                "como se dice hola en inglés",  # sin tilde
                "tradúceme al inglés",
                # Al español
                "traduce hello al español",
                "cómo se dice hello en español",
                "tradúceme al español",
                # Otros idiomas
                "cómo se dice hola en francés",
                "traduce al francés",
                "traduce esto al alemán",
            ],
            
            "CALCULAR": [
                # Multiplicación
                "cuánto es 50 por 3",
                "cuanto es 50 por 3",  # sin tilde
                "calcula 50 por 3",
                "multiplica 50 por 3",
                "50 por 3",
                # Suma
                "cuánto es 100 más 50",
                "calcula 100 más 50",
                "suma 100 más 50",
                "100 más 50",
                # Resta
                "cuánto es 100 menos 50",
                "calcula 100 menos 50",
                "resta 100 menos 50",
                # División
                "cuánto es 200 entre 4",
                "divide 200 entre 4",
                "200 entre 4",
                "200 dividido 4",
            ],
            
            "MODO_ZEN": [
                "activa modo zen",
                "modo zen",
                "modo concentración",
                "necesito concentrarme",
                "modo zen on",
                "activa zen",
                "pon modo zen",
                "quiero concentrarme",
                "modo focus",
                "activa modo focus",
                "necesito enfocarme",
            ],
        }
    
    def _generar_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Genera embeddings para todos los ejemplos de entrenamiento.
        """
        embeddings = {}
        for intent, ejemplos in self.intent_examples.items():
            embeddings[intent] = self.model.encode(ejemplos, convert_to_tensor=True)
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
