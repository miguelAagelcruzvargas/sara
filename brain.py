import os
import difflib
import webbrowser
import subprocess
import logging
import datetime
import pyautogui
import time
import re
import pyperclip
import json # Added json import for MemoryManager
import threading # Added threading import for CronosManager

# LAZY IMPORTS - Se cargan solo cuando se necesitan para inicio rápido
pywhatkit = None
genai = None
Groq = None
OpenAI = None

def _lazy_import_pywhatkit():
    """Importa pywhatkit solo cuando se necesita"""
    global pywhatkit
    if pywhatkit is None:
        try:
            import pywhatkit as pk
            pywhatkit = pk
        except ImportError:
            logging.warning("pywhatkit no disponible")
    return pywhatkit

def _lazy_import_genai():
    """Importa google.generativeai solo cuando se necesita"""
    global genai
    if genai is None:
        try:
            import google.generativeai as g
            genai = g
        except ImportError:
            logging.warning("google.generativeai no disponible")
    return genai

def _lazy_import_groq():
    """Importa Groq solo cuando se necesita"""
    global Groq
    if Groq is None:
        try:
            from groq import Groq as G
            Groq = G
        except ImportError:
            logging.warning("Groq no disponible")
    return Groq

def _lazy_import_openai():
    """Importa OpenAI solo cuando se necesita"""
    global OpenAI
    if OpenAI is None:
        try:
            from openai import OpenAI as OAI
            OpenAI = OAI
        except ImportError:
            logging.warning("OpenAI no disponible")
    return OpenAI

from config import ConfigManager
from voice import NeuralVoiceEngine
from devops import DevOpsManager
from monitor import SystemMonitor
from system_control import SystemControl
from health_monitor import HealthMonitor
from study_assistant import obtener_study_assistant
from game_controller import obtener_game_controller
from network_guardian import obtener_guardian
from network_guardian_commands import procesar_comando_guardian
from pomodoro_manager import obtener_pomodoro
from code_reviewer import obtener_reviewer
from user_profile import obtener_perfil
from calendar_module import CalendarManager
from conversation_memory import ConversationMemory
from weather_api import obtener_weather
from routines import obtener_rutinas  # NUEVO  # NUEVO
from second_brain import SecondBrain # CEREBRO VECTORIAL (NUEVO)
from intent_classifier import HybridIntentClassifier # NLU HÍBRIDO (NUEVO)
from web_agent import SaraWebSurfer # AGENTE WEB (NUEVO)

# Constantes de configuración
MAX_CHARS_VOZ = 200
MAX_CHARS_TRANSLATION = 1000

APPS_LOCALES = {
    "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
    "bloc de notas": "notepad", "notas": "notepad", "cmd": "cmd",
    "terminal": "wt", "calculadora": "calc", "control": "control",
    "explorador": "explorer", "configuracion": "start ms-settings:",
    "administrador de tareas": "taskmgr", "paint": "mspaint",
    "chrome": "chrome", "edge": "msedge", "firefox": "firefox", 
    "brave": "brave", "opera": "launcher",
    "spotify": "spotify", "discord": "discord", "steam": "steam",
    "whatsapp": "whatsapp", "telegram": "telegram", "vlc": "vlc",
    "visual studio": "code", "vscode": "code", "pycharm": "pycharm64",
    "git bash": "git-bash"
}

WEBS_COMUNES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://twitter.com",
    "instagram": "https://www.instagram.com",
    "chatgpt": "https://chat.openai.com",
    "netflix": "https://www.netflix.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "linkedin": "https://www.linkedin.com",
    "serveo": "https://serveo.net"
}

# --- MEMORIA PERSISTENTE ---
class MemoryManager:
    def __init__(self, db_file="sara_memory.json"):
        self.db_file = db_file
        self.memory = self._cargar_memoria()

    def _cargar_memoria(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return {}
        return {}

    def guardar_dato(self, clave, valor):
        self.memory[clave] = valor
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)
        return f"Entendido. He guardado '{clave}' como '{valor}'."

    def recuperar_dato(self, clave):
        # Búsqueda difusa simple
        for k, v in self.memory.items():
            if clave in k or k in clave:
                return f"Según mi memoria, {k} es: {v}"
        return "No encuentro nada relacionado en mi memoria."


# --- CRONOS (ALARMS & TIMERS) ---
class CronosManager:
    def __init__(self, brain_ref):
        self.brain = brain_ref
        self.recordatorios = [] # Tuplas (timestamp_fin, mensaje)
        self.running = True
        threading.Thread(target=self._loop_cronos, daemon=True).start()

    def programar_alarma(self, minutos, mensaje):
        fin = datetime.datetime.now() + datetime.timedelta(minutes=minutos)
        self.recordatorios.append((fin, mensaje))
        # Formato 12 horas (ej: 02:30 PM)
        hora_fin = fin.strftime("%I:%M %p")
        return f"Hecho. Te recordaré '{mensaje}' a las {hora_fin}."

    def programar_alarma_dt(self, dt, mensaje):
        """Programa alarma con datetime específico"""
        self.recordatorios.append((dt, mensaje))
        hora_fin = dt.strftime("%A %I:%M %p")
        return f"Hecho. Alarma programada para: {hora_fin}."

    def _loop_cronos(self):
        while self.running:
            now = datetime.datetime.now()
            pendientes = []
            for fin, msg in self.recordatorios:
                if now >= fin:
                    # ALARMA SUENA
                    if "Despertar" in msg:
                        # Rutina de Buenos Días (Iron Man Style)
                        hora = now.strftime("%I:%M %p")
                        saludo = f"Buenos días. Son las {hora}. Es hora de despertar y conquistar el mundo."
                        
                        # 1. Poner música suave (si pywhatkit existe)
                        if pywhatkit:
                            try: pywhatkit.playonyt("gentle morning alarm nature sounds")
                            except: pass
                        
                        # 2. Hablar
                        logging.info(f"ALARMA DESPERTADOR: {msg}")
                        self.brain.voz.hablar(saludo)
                    else:
                        # Alarma Normal
                        aviso = f"¡Atención! Recordatorio: {msg}"
                        logging.info(f"ALARMA: {msg}")
                        self.brain.voz.hablar(aviso)
                else:
                    pendientes.append((fin, msg))
            
            self.recordatorios = pendientes
            time.sleep(5) # Revisar cada 5 segundos

class SaraBrain:
    def __init__(self, splash_callback=None):
        if splash_callback:
            splash_callback(25, "Cargando configuración...", "")
        
        self.config = ConfigManager.cargar_config()
        self.ia_online = False
        self.clients = {}
        self.preferred_provider = self.config.get("provider", "Gemini")
        self.voz = NeuralVoiceEngine()
        self.devops = DevOpsManager()
        self.monitor = SystemMonitor() # Kept from original __init__
        self.memory = MemoryManager() # Cerebro a largo plazo (Clásico)
        self.cronos = CronosManager(self) # Referencia circular segura
        
        # OPTIMIZACIÓN: Inicializar Intent Classifier PRIMERO (carga el modelo)
        try:
            if splash_callback:
                splash_callback(30, "Cargando NLU...", "Modelo all-MiniLM-L6-v2")
            # Pasamos self.consultar_ia como callback para Layer 3 (AI Fallback)
            # Y splash_callback para mostrar progreso
            self.intent_classifier = HybridIntentClassifier(ia_callback=self.consultar_ia, splash_callback=splash_callback)
            logging.info("✅ HybridIntentClassifier inicializado")
        except Exception as e:
            logging.error(f"❌ Error inicializando HybridIntentClassifier: {e}")
            self.intent_classifier = None
        
        # OPTIMIZACIÓN: Pasar el modelo del NLU al Second Brain para reutilizarlo
        if splash_callback:
            splash_callback(60, "Inicializando Second Brain...", "Reutilizando modelo NLU")
        
        # Pasar el modelo del intent_classifier al second_brain si está disponible
        shared_model = None
        if self.intent_classifier and hasattr(self.intent_classifier, 'model'):
            shared_model = self.intent_classifier.model
            logging.info("🔄 Compartiendo modelo entre NLU y Second Brain")
        
        self.second_brain = SecondBrain(shared_model=shared_model) # Cerebro Vectorial (RAG)
        self.web_agent = SaraWebSurfer() # Agente Web (Playwright)
        
        # Inicializar Calendario (NUEVO)
        try:
            self.calendar = CalendarManager()
            logging.info("✅ CalendarManager inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando Calendar: {e}")
            self.calendar = None

        # Inicializar NetworkGuardian
        try:
            self.guardian = obtener_guardian(
                voice_callback=self.voz.hablar,
                ia_callback=self.consultar_ia,
                auto_start=False  # Usuario decide cuándo activar
            )
            logging.info("✅ NetworkGuardian inicializado (vigilancia manual)")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando NetworkGuardian: {e}")
            self.guardian = None
        
        # Inicializar Pomodoro Manager
        try:
            self.pomodoro = obtener_pomodoro(voice_callback=self.voz.hablar)
            logging.info("✅ PomodoroManager inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando PomodoroManager: {e}")
            self.pomodoro = None
        
        # Inicializar Code Reviewer
        try:
            self.code_reviewer = obtener_reviewer(ia_callback=self.consultar_ia)
            logging.info("✅ CodeReviewer inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando CodeReviewer: {e}")
            self.code_reviewer = None
        
        # Inicializar Health Monitor
        try:
            self.health = HealthMonitor()
            # Iniciar thread de recordatorios
            self.health_reminder_thread = threading.Thread(target=self._health_reminder_loop, daemon=True)
            self.health_reminder_thread.start()
            logging.info("✅ HealthMonitor inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando HealthMonitor: {e}")
            self.health = None
        
        # Inicializar Study Assistant
        try:
            self.study = obtener_study_assistant(ia_callback=self.consultar_ia)
            logging.info("✅ StudyAssistant inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando StudyAssistant: {e}")
            self.study = None
        
        # Inicializar Game Controller
        try:
            self.games = obtener_game_controller()
            logging.info("✅ GameController inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando GameController: {e}")
            self.games = None
        

            
        # Inicializar System Control (NUEVO)
        try:
            self.sys_control = SystemControl()
            logging.info("✅ SystemControl inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando SystemControl: {e}")
            self.sys_control = None
        
        # Inicializar User Profile
        try:
            self.perfil = obtener_perfil()
            logging.info("✅ UserProfile cargado")
        except Exception as e:
            logging.error(f"⚠️ Error cargando perfil: {e}")
            self.perfil = None
        
        # Inicializar Conversation Memory
        try:
            self.memory = ConversationMemory(max_history=10)
            logging.info("✅ ConversationMemory inicializada")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando memoria: {e}")
            self.memory = None
        
        # Inicializar Weather API (NUEVO)
        try:
            ciudad_perfil = None
            if self.perfil and self.perfil.profile["user"].get("city"):
                ciudad_perfil = self.perfil.profile["user"]["city"]
                
            self.weather = obtener_weather(city=ciudad_perfil or "Mexico City")
            logging.info(f"✅ WeatherAPI inicializada ({self.weather.city})")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando WeatherAPI: {e}")
            self.weather = None
        
        # Inicializar Rutinas (NUEVO)
        try:
            self.routines = obtener_rutinas(self)
            logging.info("✅ RoutineManager inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando rutinas: {e}")
            self.routines = None
            
        self.conectar_ias()
        self.dictation_mode = False
        
        # Asignar callback de IA al intent classifier (después de conectar_ias)
        if self.intent_classifier:
            self.intent_classifier.ia_callback = self.consultar_ia

    def conectar_ias(self):
        # Recargar configuración para obtener las API keys más recientes
        self.config = ConfigManager.cargar_config()
        
        self.clients = {}
        
        # GEMINI
        k_gem = self.config.get("gemini_key")
        if k_gem:
            # Lazy import de genai
            genai_lib = _lazy_import_genai()
            if genai_lib:
                try:
                    genai_lib.configure(api_key=k_gem)
                    # Lista de modelos a probar (en orden de prioridad/gratuidad)
                    modelos_candidatos = [
                        'gemini-2.0-flash-exp',       # Experimental suele ser gratis
                        'gemini-2.0-flash-lite-preview-02-05', # Lite es eficiente
                        'gemini-1.5-flash',           # Estándar actual
                        'gemini-pro',                 # Legacy
                        'gemini-2.0-flash'            # Último recurso (puede tener cuota 0)
                    ]
                    
                    modelo_seleccionado = None
                    
                    # Probar modelos disponibles
                    try:
                        disponibles = [m.name for m in genai_lib.list_models()]
                        for candidato in modelos_candidatos:
                            # Buscar coincidencia exacta o parcial (ej: context/models/)
                            if any(candidato in m for m in disponibles):
                                modelo_seleccionado = candidato
                                break
                    except: pass
                    
                    # Si no se encontró ninguno de la lista, usar fallback
                    if not modelo_seleccionado:
                        modelo_seleccionado = 'gemini-2.0-flash-exp'
                    
                    self.clients["Gemini"] = genai_lib.GenerativeModel(
                        modelo_seleccionado,
                        system_instruction="Eres SARA, un asistente de IA avanzado. Tus respuestas son precisas y profesionales."
                    )
                    logging.info(f"✅ Gemini conectado exitosamente ({modelo_seleccionado})")
                except Exception as e:
                    logging.warning(f"Error conectando Gemini: {e}")
            else:
                logging.warning("Gemini Key detectada pero la librería 'google-generative-ai' no está instalada.")
        
        # GROQ
        k_groq = self.config.get("groq_key")
        if k_groq:
            # Lazy import de Groq
            Groq_class = _lazy_import_groq()
            if Groq_class:
                try:
                    self.clients["Groq"] = Groq_class(api_key=k_groq)
                    logging.info("✅ Groq conectado exitosamente")
                except Exception as e:
                    logging.warning(f"Error conectando Groq: {e}")

        # OPENAI
        k_openai = self.config.get("openai_key")
        if k_openai:
            # Lazy import de OpenAI
            OpenAI_class = _lazy_import_openai()
            if OpenAI_class:
                try:
                    self.clients["ChatGPT"] = OpenAI_class(api_key=k_openai)
                    logging.info("✅ OpenAI conectado exitosamente")
                except Exception as e:
                    logging.warning(f"Error conectando OpenAI: {e}")

        self.ia_online = len(self.clients) > 0
        
        # Actualizar proveedor preferido desde config
        nuevo_provider = self.config.get("provider", "Gemini")
        
        # Corrección: Si el proveedor preferido falló pero hay otros, cambiar al que funcione
        if nuevo_provider not in self.clients and self.clients:
            nuevo_provider = list(self.clients.keys())[0]
            logging.info(f"⚠️ Provider '{self.config.get('provider')}' falló. Usando '{nuevo_provider}' en su lugar.")
        
        self.preferred_provider = nuevo_provider
            
        return self.ia_online

    def consultar_ia(self, prompt, contexto_extra=""):
        if not self.ia_online: 
            return "⚠️ Modo Offline. Ve a 'Configuración' y agrega tus API Keys (Gemini, Groq o OpenAI) para activar la IA.", "error"
        
        # --- SECOND BRAIN CONTEXT INJECTION ---
        contexto_rag = ""
        if self.second_brain:
             memories = self.second_brain.recordar(prompt)
             if memories:
                 contexto_rag = "\n[MEMORIA A LARGO PLAZO RECUPERADA]:\n" + "\n".join(memories) + "\n"
        
        full_prompt = f"{contexto_rag}{prompt} {contexto_extra}"
        providers = [self.preferred_provider] + [k for k in self.clients.keys() if k != self.preferred_provider]
        
        errores_limite = []  # Guardar errores de límite para reportar
        
        for p in providers:
            if p in self.clients:
                try:
                    if p == "Gemini": 
                        # GEMINI: Soporta JSON mode nativo en modelos nuevos, pero usaremos texto estructurado por compatibilidad
                        return self.clients[p].generate_content(full_prompt).text, "ai"
                    else: 
                        model = "llama-3.3-70b-versatile" if p == "Groq" else "gpt-4o-mini"
                        
                        # Configurar respuesta JSON si se solicita explícitamente en el prompt
                        response_format = {"type": "json_object"} if "JSON" in full_prompt else None
                        
                        resp = self.clients[p].chat.completions.create(
                            messages=[
                                {"role": "system", "content": "Eres SARA. Responde brevemente. Si se pide JSON, entrega SOLO JSON válido."}, 
                                {"role": "user", "content": full_prompt}
                            ],
                            model=model,
                            response_format=response_format
                        )
                        return resp.choices[0].message.content, "ai"
                        
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Detectar errores de límite de uso
                    if any(x in error_str for x in ["quota", "limit", "rate limit", "429", "resource exhausted", "too many requests"]):
                        mensaje_limite = self._generar_mensaje_limite(p, error_str)
                        errores_limite.append((p, mensaje_limite))
                        logging.warning(f"⚠️ Límite alcanzado en {p}: {error_str}")
                        continue
                    
                    # Detectar errores de autenticación
                    elif any(x in error_str for x in ["invalid api key", "unauthorized", "401", "403", "authentication"]):
                        logging.error(f"❌ API Key inválida para {p}: {error_str}")
                        continue
                    
                    # Otros errores
                    else:
                        logging.error(f"Fallo IA {p}: {e}")
                        continue
        
        # Si todos fallaron por límite, dar mensaje específico
        if errores_limite:
            if len(errores_limite) == len(providers):
                # Todos los proveedores alcanzaron el límite
                return self._mensaje_todos_limites_alcanzados(errores_limite), "error"
            else:
                # Algunos alcanzaron límite, otros fallaron
                return errores_limite[0][1], "error"
        
        # Si llegamos aquí, todos fallaron por otras razones
        return "❌ Error: Todas las IAs fallaron. Verifica tus API Keys en Configuración.", "error"
    
    def _generar_mensaje_limite(self, provider, error_str):
        """Genera un mensaje amigable cuando se alcanza el límite de una API"""
        
        mensajes = {
            "Gemini": "⏰ Límite de uso de Gemini alcanzado.\n\n"
                     "💡 Opciones:\n"
                     "1. Espera unos minutos (límite por minuto)\n"
                     "2. Usa otra API (Groq o OpenAI) desde Configuración\n"
                     "3. Si es límite diario, vuelve mañana\n\n"
                     "📊 Gemini Free: 15 requests/minuto, 1500/día",
            
            "Groq": "⏰ Límite de uso de Groq alcanzado.\n\n"
                   "💡 Opciones:\n"
                   "1. Espera 1 minuto (límite: 30 req/min)\n"
                   "2. Usa Gemini desde Configuración\n"
                   "3. Upgrade a Groq Pro para más requests\n\n"
                   "📊 Groq Free: 30 requests/minuto, 14,400/día",
            
            "ChatGPT": "⏰ Límite de uso de OpenAI alcanzado.\n\n"
                      "💡 Opciones:\n"
                      "1. Revisa tu plan en platform.openai.com\n"
                      "2. Usa Gemini (gratis) desde Configuración\n"
                      "3. Recarga créditos si es necesario\n\n"
                      "📊 OpenAI: Límites según tu plan de pago"
        }
        
        return mensajes.get(provider, f"⏰ Límite de uso alcanzado en {provider}.\n\nPrueba con otro proveedor desde Configuración.")
    
    def _mensaje_todos_limites_alcanzados(self, errores):
        """Mensaje cuando todos los proveedores alcanzaron su límite"""
        providers_afectados = [p for p, _ in errores]
        
        mensaje = "⏰ LÍMITES ALCANZADOS EN TODOS LOS PROVEEDORES\n\n"
        mensaje += f"Proveedores afectados: {', '.join(providers_afectados)}\n\n"
        mensaje += "💡 Recomendaciones:\n"
        mensaje += "1. Espera unos minutos y vuelve a intentar\n"
        mensaje += "2. Usa comandos locales (sistema, git, abrir apps)\n"
        mensaje += "3. Si usas mucho SARA, considera:\n"
        mensaje += "   • Groq Pro (más requests)\n"
        mensaje += "   • OpenAI con créditos\n"
        mensaje += "   • Múltiples API keys rotativas\n\n"
        mensaje += "⚙️ Mientras tanto, sigo operativa para comandos que no requieren IA."
        
        return mensaje

    def abrir_inteligente(self, objetivo, comando_completo=""):
        objetivo = objetivo.lower().strip()
        
        # 1. Modo Búsqueda
        if "busca" in comando_completo or "buscar" in comando_completo:
            if "youtube" in objetivo:
                q = comando_completo.replace("busca", "").replace("en youtube", "").replace("videos de", "").strip()
                webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
                return f"YouTube: {q}", "local"
            q = comando_completo.replace("busca", "").replace("en google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={q}")
            return f"Google: {q}", "local"

        # 2. Apps Locales (Coincidencia Difusa)
        matches = difflib.get_close_matches(objetivo, APPS_LOCALES.keys(), n=1, cutoff=0.5)
        if matches:
            app = matches[0]
            try:
                subprocess.Popen(f"start {APPS_LOCALES[app]}", shell=True)
                return f"Iniciando {app}...", "local"
            except Exception as e:
                logging.error(f"Error abriendo aplicación {app}: {e}")
                return f"Error al abrir {app}.", "error"

        # 3. Webs
        matches_web = difflib.get_close_matches(objetivo, WEBS_COMUNES.keys(), n=1, cutoff=0.5)
        if matches_web:
            web = matches_web[0]
            webbrowser.open(WEBS_COMUNES[web])
            return f"Navegando a {web}...", "local"

        # 4. Fallback IA
        if self.ia_online:
            p = f"El usuario quiere abrir '{objetivo}'. Si es una web, dame SOLO la URL. Si no, di 'NO'."
            resp, _ = self.consultar_ia(p)
            if "http" in resp:
                webbrowser.open(resp.strip())
                return f"Abriendo recomendación IA: {objetivo}", "ai"
        
        return f"No pude encontrar '{objetivo}'.", "error"

    def ver_pantalla(self, prompt_usuario):
        """Captura pantalla y la envía a la IA (Gemini Vision)"""
        if not self.ia_online: return "❌ IA Offline. No puedo ver.", "error"
        
        # Guardar screenshot temporal
        try:
            screenshot = pyautogui.screenshot()
            
            # Usar Gemini
            if "Gemini" in self.clients:
                model = self.clients["Gemini"]
                
                # Prompt mejorado
                prompt_base = f"El usuario dice: '{prompt_usuario}'. Analiza la captura de pantalla y responde concisamente."
                
                response = model.generate_content([prompt_base, screenshot])
                return response.text, "ai"
            else:
                 return "❌ Solo Gemini soporta visión por ahora. Cambia el proveedor en Configuración.", "error"
        except Exception as e:
            return f"❌ Error en visión: {e}", "error"

    def procesar_comando_git_completo(self, comando):
        """Detecta y ejecuta comandos Git complejos automáticamente."""
        cmd = comando.lower()
        resultado_final = ""
        acciones_realizadas = []
        
        # Usar IA para entender mejor la intención si está disponible
        mensaje_commit = "Update automático SARA"
        
        if self.ia_online:
            try:
                prompt_ia = f"""El usuario dijo: "{comando}"
Analiza la intención. Responde SOLO JSON válido:
{{
  "necesita_init": true/false,
  "quiere_subir": true/false,
  "mensaje_commit": "mensaje si menciona, sino 'Update automático SARA'"
}}"""
                respuesta_ia = self.consultar_ia(prompt_ia, "")[0]
                import json as json_lib
                try:
                    respuesta_limpia = respuesta_ia.strip()
                    if "```" in respuesta_limpia:
                        respuesta_limpia = respuesta_limpia.split("```")[1].replace("json", "")
                    start = respuesta_limpia.find('{')
                    end = respuesta_limpia.rfind('}') + 1
                    datos = json_lib.loads(respuesta_limpia[start:end])
                    if datos.get("mensaje_commit"): mensaje_commit = datos["mensaje_commit"]
                except: pass
            except: pass
        
        necesita_init = any(x in cmd for x in ["inicializar", "git init", "init"])
        quiere_subir = any(x in cmd for x in ["subir", "push", "upload"])
        quiere_commit = any(x in cmd for x in ["commit", "guardar"])
        
        # Lógica de ejecución
        if necesita_init and not DevOpsManager._es_repositorio_git():
            resultado_final += DevOpsManager.git_init() + "\n"
            acciones_realizadas.append("init")
            
        if (quiere_commit or quiere_subir) and DevOpsManager._es_repositorio_git():
             # En la versión corregida, git_smart_push maneja add/commit/push
            if quiere_subir:
                resultado_final += DevOpsManager.git_smart_push(mensaje_commit)
                acciones_realizadas.append("push")
            else:
                # Solo commit
                DevOpsManager._ejecutar_git(["add", "."])
                c, out, err = DevOpsManager._ejecutar_git(["commit", "-m", mensaje_commit])
                resultado_final += f"Commit: {out}\n" if c == 0 else f"Error commit: {err}\n"
                acciones_realizadas.append("commit")

        if acciones_realizadas:
            return f"✅ Tareas Git completadas:\n{resultado_final}"
        else:
            return "⚠️ No se realizaron acciones Git. Verifica el comando."
    
    def _health_reminder_loop(self):
        """Loop en background que verifica recordatorios de salud"""
        while True:
            try:
                if self.health and self.health.is_active:
                    reminder = self.health.check_reminders()
                    if reminder:
                        emoji, title, message = reminder
                        # Notificar por voz
                        self.voz.hablar(message)
                        logging.info(f"🏥 Recordatorio de salud: {title}")
                
                time.sleep(30)  # Verificar cada 30 segundos
            except Exception as e:
                logging.error(f"Error en health reminder loop: {e}")
                time.sleep(60)


    def _es_similar(self, texto, keywords, umbral=0.8):
        """Devuelve True si alguna palabra del texto se parece a las keywords"""
        words = texto.split()
        for w in words:
            # Cotejar contra cada keyword
            matches = difflib.get_close_matches(w, keywords, n=1, cutoff=umbral)
            if matches:
                logging.debug(f"Fuzzy match: '{w}' -> '{matches[0]}'")
                return True
        return False
    
    def _procesar_con_nlu(self, comando):
        """
        Procesa comandos usando el sistema híbrido de NLU (3 capas).
        Retorna (respuesta, tipo) o None si no se pudo procesar.
        """
        if not self.intent_classifier:
            return None
        
        # Clasificar intención
        intent, params, source = self.intent_classifier.clasificar(comando)
        logging.info(f"🎯 Intent: {intent} | Source: {source} | Params: {params}")
        
        # Etiqueta visual para depuración
        tag = ""
        if source == "ml": tag = "[ML] "
        elif source == "ai": tag = "[AI] "
        # Pattern match no lleva tag para no ensuciar comandos comunes
        
        # Ejecutar según intención
        if intent == "MEMORIZAR":
            if self.second_brain:
                res = self.second_brain.memorizar(params.get("data", ""))
                return f"✅ {res}", "sara"
        
        elif intent == "VOLUMEN_SUBIR":
            if self.sys_control:
                amount = params.get("amount", 10)
                return self.sys_control.adjust_volume(amount), "sys"
        
        elif intent == "VOLUMEN_BAJAR":
            if self.sys_control:
                amount = params.get("amount", 10)
                return self.sys_control.adjust_volume(-amount), "sys"
        
        elif intent == "SILENCIO":
            if self.sys_control:
                return self.sys_control.mute_volume(), "sys"
        
        elif intent == "ABRIR_APP":
            app_name = params.get("app_name", "")
            return self.abrir_inteligente(app_name, comando)
        
        elif intent == "BUSCAR_WEB":
            if self.web_agent:
                query = params.get("query", "")
                res = self.web_agent.buscar_google(query)
                if self.ia_online:
                    resumen_ia, _ = self.consultar_ia(f"Resume esta investigación web:\\n{res}")
                    return resumen_ia, "sara"
                return f"🔎 Resultados:\\n{res}", "sara"
        
        elif intent == "LEER_DOCUMENTO":
            if self.web_agent:
                url = pyperclip.paste().strip()
                if "http" in url:
                    contenido = self.web_agent.leer_pagina(url)
                    if self.ia_online:
                        resumen_ia, _ = self.consultar_ia(f"Resume este contenido:\\n{contenido}")
                        return resumen_ia, "sara"
                    return f"📄 Contenido:\\n{contenido[:500]}...", "sara"
                else:
                    return "Copia la URL primero (Ctrl+C) y vuelve a preguntar.", "sara"
        
        elif intent == "REPRODUCIR_MEDIA":
            query = params.get("query", "")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"🎵 Reproduciendo: {query}", "media"
        
        elif intent == "ALARMA":
            if self.cronos:
                minutes = params.get("minutes", 5)
                message = params.get("message", "Alarma")
                return self.cronos.programar_alarma(minutes, message), "sara"
        
        elif intent == "CLIMA":
            if self.weather:
                return self.weather.get_current_weather(), "weather"
        
        elif intent == "HORA_FECHA":
            tipo = params.get("type", "hora")
            if tipo == "hora":
                return f"🕐 Son las {datetime.datetime.now().strftime('%H:%M')}", "sara"
            else:
                return f"📅 Hoy es {datetime.datetime.now().strftime('%d de %B de %Y')}", "sara"
        
        elif intent == "TRADUCIR":
            text = params.get("text", "")
            target_lang = params.get("target_lang", "en")
            if self.ia_online:
                prompt = f"Traduce al {'inglés' if target_lang == 'en' else 'español'}: {text}"
                return self.consultar_ia(prompt)
        
        elif intent == "CALCULAR":
            expr = params.get("expression", "")
            try:
                # Evaluar expresión matemática de forma segura
                resultado = eval(expr, {"__builtins__": {}}, {})
                return f"🔢 Resultado: {resultado}", "sara"
            except:
                return "No pude calcular eso. Intenta con una expresión más simple.", "sara"
        
        elif intent == "MODO_ZEN":
            if self.sys_control:
                self.sys_control.minimize_all_windows()
                time.sleep(0.5)
                webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk")
                return "🧘‍♂️ Modo Zen activado.", "sara"
        
        elif intent == "CONVERSACION":
            # Delegar a IA
            if self.ia_online:
                return self.consultar_ia(params.get("text", comando))
        
        return None



    def procesar(self, comando):
        cmd = comando.lower()
        
        # === PRIORIDAD 1: INTENTAR NLU HÍBRIDO ===
        if self.intent_classifier:
            resultado_nlu = self._procesar_con_nlu(comando)
            if resultado_nlu:
                # Guardar en memoria conversacional
                if self.memory:
                    self.memory.add_turn(comando, resultado_nlu[0])
                return resultado_nlu
        
        # === PRIORIDAD 2: COMANDOS ESPECIALIZADOS (que no están en NLU) ===
        
        # --- COMMANDOS DE MEMORIA (SECOND BRAIN) - Lectura de documentos ---
        if self.second_brain:
            if "lee este documento" in cmd or "lee este archivo" in cmd:
                ruta = pyperclip.paste().replace('"', '')
                if os.path.exists(ruta):
                    res = self.second_brain.ingestar_archivo(ruta)
                    return f"📄 {res}", "sara"
                else:
                    return "Copia la ruta del archivo primero (Ctrl+C) y vuelve a decirme.", "sara"

            
            # 2. Lectura de documentos (Arrastrar y soltar mental o ruta)
            if "lee este documento" in cmd or "lee este archivo" in cmd:
                # Intentar leer desde el portapapeles si es una ruta
                ruta = pyperclip.paste().replace('"', '')
                if os.path.exists(ruta):
                    res = self.second_brain.ingestar_archivo(ruta)
                    return f"📄 {res}", "sara"
                else:
                    return "Copia la ruta del archivo primero (Ctrl+C) y vuelve a decirme.", "sara"

        # --- AGENTE WEB (PLAYWRIGHT) ---
        if self.web_agent:
            # 1. Investigación Web
            if "investiga sobre" in cmd or "investiga" in cmd:
                tema = cmd.replace("investiga sobre", "").replace("investiga", "").replace("sara", "").strip()
                res = self.web_agent.buscar_google(tema)
                
                # Resumir con IA
                if self.ia_online:
                    resumen_ia, _ = self.consultar_ia(f"Resume esta investigación web para el usuario:\n{res}")
                    return resumen_ia, "sara"
                return f"🔎 Resultados:\n{res}", "sara"
            
            # 2. Leer Página
            if "lee esta página" in cmd or "qué dice esta página" in cmd or "que dice esta pagina" in cmd:
                 # Intentar leer URL del portapapeles
                url = pyperclip.paste().strip()
                if "http" in url:
                    contenido = self.web_agent.leer_pagina(url)
                    # Resumir con IA
                    if self.ia_online:
                        resumen_ia, _ = self.consultar_ia(f"Resume este contenido web en 3 puntos clave:\n{contenido}")
                        return resumen_ia, "sara"
                    return f"📄 Contenido:\n{contenido[:500]}...", "sara"
                else:
                    return "Copia la URL primero (Ctrl+C) y vuelve a preguntar.", "sara"

        # === MEMORIA CONTEXTUAL (NUEVO) ===
        # Detectar si es pregunta de seguimiento
        contexto_adicional = ""
        if self.memory and self.memory.is_follow_up_question(comando):
            contexto_adicional = self.memory.get_context_prompt(include_last_n=2)
            logging.debug(f"Pregunta de seguimiento detectada. Tema: {self.memory.get_last_topic()}")

        # --- CONTROL DE VOLUMEN DIRECTO (SIN IA) ---
        if self.sys_control:
            if any(x in cmd for x in ["sube el volumen", "subele volumen", "sube volumen", "súbele volumen"]):
                return self.sys_control.adjust_volume(10), "sys"
            elif any(x in cmd for x in ["baja el volumen", "bájale volumen", "baja volumen"]):
                return self.sys_control.adjust_volume(-10), "sys"
            elif "silencio" in cmd or "mute" in cmd:
                return self.sys_control.mute_volume(), "sys"

        # --- NETWORKGUARDIAN (ANTES DE TODO) ---
        if self.guardian and any(x in cmd for x in [
            "vigilancia", "dispositivos", "red", "fortaleza", "wifi", "panel",
            "alertas", "tráfico", "consumidores", "conexiones",
            "confía", "confiar", "sospechoso", "renombrar dispositivo",
            "dashboard", "escanear"
        ]):
            resultado = procesar_comando_guardian(cmd, self.guardian)
            if resultado:
                # Guardar en memoria
                if self.memory:
                    self.memory.add_turn(comando, resultado, intent="network")
                return resultado

        # --- RUTINAS (NUEVO) ---
        es_rutina = self._es_similar(cmd, ["rutina", "modo", "escena"], 0.8)
        if self.routines and (es_rutina or "rutina" in cmd or "modo" in cmd):
            # Ej: "ejecuta rutina buenos días" o "activa modo trabajo"
            if "rutina" in cmd:
                nombre_rutina = cmd.split("rutina")[-1].strip()
            elif "modo" in cmd:
                nombre_rutina = "modo_" + cmd.split("modo")[-1].strip()
            else:
                nombre_rutina = cmd
                
            if any(x in nombre_rutina for x in ["buenos dias", "buenos días", "mañana"]):
                return self.routines.execute_routine("buenos_dias"), "sara"
            elif "trabajo" in nombre_rutina:
                return self.routines.execute_routine("modo_trabajo"), "sara"
            elif "fin" in nombre_rutina or "descanso" in nombre_rutina:
                return self.routines.execute_routine("fin_trabajo"), "sara"
            elif "lista" in cmd or "disponibles" in cmd:
                return self.routines.get_available_routines(), "sara"

        # --- CALENDARIO / AGENDA (NUEVO) ---
        keywords_agenda = ["agenda", "eventos", "calendario", "que tengo", "qué tengo", "reunión", "cita", "compromiso"]
        if self._es_similar(cmd, keywords_agenda, 0.8) or "agenda" in cmd or "calendario" in cmd:
            # CONSULTA
            if any(x in cmd for x in ["que tengo", "qué tengo", "ver", "lee", "dime", "hoy", "mañana", "próximos"]):
                if self.calendar:
                    return self.calendar.get_next_events(), "sara"
                else:
                    return "No tengo acceso a tu calendario. Verifica las credenciales.", "sara"
            
            # CREACIÓN (Básico)
            # Ej: "Agendar reunión mañana a las 5" (requiere parsing complejo, por ahora delegamos a IA o pedimos formato especifico)
            # Para esta iteración, solo consulta. La creación por voz natural es compleja sin un parser de fechas robusto.
        
        # --- CLIMA / TIEMPO (NUEVO) ---
        keywords_clima = ["clima", "tiempo", "temperatura", "pronóstico", "llover", "lluvia", 
                         "calor", "frío", "frio", "va a estar", "van a estar"]
                         
        if self.weather and (self._es_similar(cmd, keywords_clima, 0.75) or 
                            (self.memory and self.memory.get_last_topic() == "clima" and self.memory.is_follow_up_question(comando))):
            
            ciudad = None
            # Intentar extraer ciudad del comando (muy básico)
            if " en " in cmd:
                ciudad = cmd.split(" en ")[1].strip()
            
            if any(x in cmd for x in ["pronóstico", "mañana", "semana", "va a estar", "llover", "lluvia"]):
                resultado = self.weather.get_forecast(city=ciudad)
            else:
                resultado = self.weather.get_current_weather(city=ciudad)
                
            # Guardar en memoria
            if self.memory:
                self.memory.add_turn(comando, resultado, intent="weather")
            return resultado, "sara"

        # --- CAMBIO DE UBICACIÓN (NUEVO) ---
        # --- CAMBIO DE UBICACIÓN (NUEVO) ---
        cmd_limpio = cmd.replace("á", "a").replace("ó", "o") # Normalizar acentos basicos para chequeo
        keywords_ubicacion = ["cambia mi ubicacion a", "cambia mi ciudad a", "configura mi ciudad en", 
                           "cambia mi cuidad a", "cambiar mi ciudad a", # Errores comunes
                           "pon mi ciudad en", "pon mi ubicacion en"]
                           
        if any(k in cmd_limpio for k in keywords_ubicacion):
            # Extraer ciudad eliminando la frase clave que coincidió
            nueva_ciudad = cmd
            for k in keywords_ubicacion:
                 if k in cmd_limpio:
                     # Reemplazo insensible a mayusculas/acentos es complejo, hacemos un split simple
                     # O mejor, usamos la longitud de la keyword encontrada
                     idx = cmd_limpio.find(k)
                     if idx != -1:
                        nueva_ciudad = cmd[idx + len(k):].strip()
                        break
            
            if nueva_ciudad:
                # Actualizar perfil
                if self.perfil:
                    self.perfil.update_user_info(city=nueva_ciudad)
                # Actualizar API clima
                if self.weather:
                    self.weather.city = nueva_ciudad
                
                return f"✅ Ubicación actualizada a: {nueva_ciudad}. Ahora te daré el clima de ahí.", "sara"
            else:
                # Si se cortó el comando (ej: "Sara cambia mi ciudad a...")
                if self.memory:
                    self.memory.add_turn(comando, "¿A qué ciudad?", intent="location_change")
                return "No te escuché bien. ¿A qué ciudad quieres cambiar?", "sara"

        # --- NUEVO: SMART INTENT ROUTER (LLM DECIDE) ---
        # Si la IA está online, usamos el Router Inteligente para comandos complejos
        if self.ia_online:
            # Detectar comandos locales rápidos para no gastar IA innecesariamente
            # Quitamos "play" para que el Router decida si es spotify o youtube
            es_comando_rapido = any(x in cmd for x in ["hora", "fecha", "sistema", "monitor", "mute", "silencio", "volumen", "sube", "baja", "súbele", "bájale", "zen", "sen", "sem", "cen"])
            
            if not es_comando_rapido:
                try:
                    # Prompt del Router

                    prompt_router = f"""Analiza el comando: "{cmd}"
                    Responde SOLO un objeto JSON con las acciones.
                    Acciones posibles:
                    - "search_web": {{ "query": "lo que busca", "site": "youtube/google" }}
                    - "open_app": {{ "app_name": "nombre app" }}
                    - "volume": {{ "level": 0-100 (int) }} o {{ "change": +/- int }}
                    - "brightness": {{ "level": 0-100 (int) }}
                    - "media": "play_pause" / "next" / "prev" / "mute"
                    - "timer": {{ "minutes": int, "message": "msg" }}
                    - "zen_mode": {{ "enable": true/false }}
                    - "chat": "respuesta conversacional si no es acción"
                    
                    Ejemplo: "Sube volumen al 50 y pon rock"
                    [
                      {{ "action": "volume", "level": 50 }},
                      {{ "action": "search_web", "query": "rock music", "site": "youtube" }}
                    ]
                    """
                    
                    resp_json, _ = self.consultar_ia(prompt_router)
                    
                    # Intentar parsear JSON
                    import json
                    # Limpiar markdown si existe
                    if "```" in resp_json:
                        resp_json = resp_json.split("```")[1].replace("json", "").strip()
                    
                    acciones = json.loads(resp_json)
                    
                    # Si la IA responde un chat normal (str) o lista vacía
                    if isinstance(acciones, str):
                        return acciones, "ai"
                        
                    resultados = []
                    es_accion_valida = False
                    
                    if isinstance(acciones, list):
                        for accion in acciones:
                            tipo = accion.get("action")
                            es_accion_valida = True
                            
                            if tipo == "volume":
                                if "level" in accion:
                                    resultados.append(self.sys_control.set_volume(int(accion["level"])))
                                elif "change" in accion:
                                    resultados.append(self.sys_control.adjust_volume(int(accion["change"])))
                                    
                            elif tipo == "brightness":
                                resultados.append(self.sys_control.set_brightness(int(accion["level"])))
                                
                            elif tipo == "media":
                                op = accion.get("value") or accion.get("operation") or "play_pause" # Robustez
                                if op == "play_pause": resultados.append(self.sys_control.media_play_pause())
                                elif op == "next": resultados.append(self.sys_control.media_next())
                                elif op == "prev": resultados.append(self.sys_control.media_prev())
                                elif op == "mute": resultados.append(self.sys_control.mute_volume())

                            elif tipo == "open_app":
                                resultados.append(self.abrir_inteligente(accion["app_name"], cmd)[0])

                            elif tipo == "search_web":
                                q = accion["query"]
                                site = accion.get("site", "google")
                                if site == "youtube":
                                    webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
                                else:
                                    webbrowser.open(f"https://www.google.com/search?q={q}")
                                resultados.append(f"Buscando {q} en {site}")

                            elif tipo == "timer":
                                resultados.append(self.cronos.programar_alarma(accion["minutes"], accion.get("message", "Alarma")))
                            
                            elif tipo == "zen_mode":
                                enable = accion.get("enable", True)
                                self.sys_control.minimize_all_windows()
                                if enable:
                                    time.sleep(0.5)
                                    webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk")
                                    resultados.append("🧘‍♂️ Modo Zen activado por IA.")
                                else:
                                    # Intentar cerrar musica
                                    self.sys_control.close_window_by_title("lofi")
                                    self.sys_control.close_window_by_title("youtube")
                                    resultados.append("🧘‍♂️ Modo Zen desactivado.")

                            elif tipo == "chat":
                                return accion.get("response", "Entendido."), "ai"

                    if es_accion_valida and resultados:
                        return " | ".join(resultados), "sys"
                        
                except Exception as e:
                    logging.error(f"Fallo Smart Router: {e}")
                    # Fallback a lógica antigua
                    pass

        # --- GESTIÓN DE DIRECTORIO ---
        if any(x in cmd for x in ["trabajar en", "cambiar directorio", "cambiar carpeta"]):
            ruta = cmd.replace("trabajar en", "").replace("cambiar directorio", "").replace("cambiar carpeta", "").strip()
            # Limpiar comillas
            ruta = ruta.replace('"', '').replace("'", "")
            # Expansión de atajos
            if "documentos" in ruta: ruta = os.path.expanduser("~/Documents")
            elif "escritorio" in ruta: ruta = os.path.expanduser("~/Desktop")
            elif "descargas" in ruta: ruta = os.path.expanduser("~/Downloads")
            elif "usuario" in ruta: ruta = os.path.expanduser("~")
            
            # Ejecutar cambio de directorio y analizar contexto
            res_dir = self.devops.set_work_dir(ruta)
            
            # Análisis Proactivo
            reporte, sugerencia = self.devops.analizar_estado_git()
            
            respuesta = f"{res_dir}\n{reporte}"
            if sugerencia == "init":
                respuesta += "\n💡 ¿Quieres inicializar un repositorio aquí?"
            elif sugerencia == "commit":
                respuesta += "\n💡 Hay cambios pendientes. Di 'subir cambios' para guardarlos."
            elif sugerencia == "push":
                respuesta += "\n💡 Tienes commits locales. Di 'subir cambios' para enviarlos."
                
            return respuesta, "dev"

        # --- DETECCIÓN DE COMANDOS COMPLEJOS ---
        acciones_git = sum([
            "git" in cmd or "repo" in cmd,
            any(x in cmd for x in ["inicializar", "init", "crear"]),
            any(x in cmd for x in ["subir", "push", "upload"]),
            any(x in cmd for x in ["commit", "guardar"])
        ])
        
        if acciones_git >= 2:
            return self.procesar_comando_git_completo(comando), "dev"

        # --- SECCIÓN DEVOPS AVANZADA (NUEVO) ---
        if "puertos abiertos" in cmd or "quien usa" in cmd:
            # Extraer puerto
            puerto = "".join([c for c in cmd if c.isdigit()])
            if not puerto: return "❌ Dime qué puerto (ej: 'quien usa el 8080').", "error"
            return SystemOps.quien_usa_puerto(puerto), "sys"

        elif "libera el puerto" in cmd or "matar puerto" in cmd:
            puerto = "".join([c for c in cmd if c.isdigit()])
            if not puerto: return "❌ Dime qué puerto liberar.", "error"
            return SystemOps.liberar_puerto(puerto), "sys"

        elif "mi ip" in cmd:
            return f"{SystemOps.obtener_ip_local()}\n{SystemOps.obtener_ip_publica()}", "sys"

        elif "instalar dependencias" in cmd or "instalar paquetes" in cmd:
            code, out, err = BuildManager.instalar_dependencias()
            return f"📦 Resultado Instalación:\n{out}\n{err}", "dev"

        elif "construir proyecto" in cmd or "build" in cmd:
            code, out, err = BuildManager.construir_proyecto()
            return f"🔨 Build Terminado:\n{out}", "dev"

        # --- MULTIMEDIA (FALLBACK WEB) ---
        # Si no hay IA o falló el router, y piden música -> YouTube Web
        # Esto responde a la duda del usuario: "¿Qué pasa si no tengo Spotify?"
        keywords_musica = ["pon", "play", "reproduce", "escuchar", "quiero oir"]
        if any(cmd.startswith(k + " ") for k in keywords_musica) or "youtube" in cmd:
            busqueda = cmd
            for k in keywords_musica:
                busqueda = busqueda.replace(k, "")
            
            busqueda = busqueda.replace("musica", "").replace("música", "").replace("en youtube", "").strip()
            
            if busqueda:
                import webbrowser
                # Buscar en YouTube
                webbrowser.open(f"https://www.youtube.com/results?search_query={busqueda}")
                return f"🎵 Buscando '{busqueda}' en YouTube...", "sara"
            return f"🏗️ Resultado Build:\n{out}\n{err}", "dev"

        # --- SECCIÓN GIT CLÁSICA ---
        if "git push" in cmd or "subir cambios" in cmd:
            mensaje = cmd.replace("git push", "").replace("subir cambios", "").strip()
            if not mensaje: mensaje = "Update automático SARA"
            return self.devops.git_smart_push(mensaje), "dev"
        
        elif "git status" in cmd:
            return self.devops.git_status(), "dev"
        
        elif "inicializar git" in cmd or "git init" in cmd:
            return self.devops.git_init(), "dev"
        
        elif "git ramas" in cmd or "listar ramas" in cmd:
            return self.devops.git_listar_ramas(), "dev"
        
        elif "cambiar rama" in cmd or "git checkout" in cmd:
            nombre = cmd.replace("cambiar rama", "").replace("git checkout", "").strip()
            return self.devops.git_cambiar_rama(nombre), "dev"
        
        elif "crear rama" in cmd or "git branch" in cmd and "nueva" in cmd:
            nombre = cmd.replace("crear rama", "").replace("git branch", "").replace("nueva", "").strip()
            return self.devops.git_crear_rama(nombre), "dev"
        
        elif "git pull" in cmd or "traer cambios" in cmd:
            return self.devops.git_pull(), "dev"
        
        elif "git ayuda" in cmd:
            ayuda = "📚 COMANDOS GIT:\n" + "="*30 + "\n"
            ayuda += "• 'trabajar en [ruta]' (Cambia carpeta)\n"
            ayuda += "• 'git status', 'git init'\n"
            ayuda += "• 'git push' (Sube todo auto)\n"
            ayuda += "• 'git pull', 'crear rama [nombre]'\n"
            return ayuda, "dev"
            
        # --- AYUDA GENERAL (NUEVO) ---
        elif "ayuda" in cmd or "comandos" in cmd or "que puedes hacer" in cmd:
            ayuda = "🤖 COMANDOS DISPONIBLES:\n" + "="*25 + "\n"
            
            ayuda += "⚡ RÁPIDOS (Local):\n"
            ayuda += "• 'Hola', 'Gracias', 'Hora', 'Fecha'\n"
            ayuda += "• 'Calcula 50*3', 'Abre [app]'\n\n"
            
            ayuda += "🦾 IRON MAN (Control PC):\n"
            ayuda += "• 'Modo dictado' (Escribe por ti)\n"
            ayuda += "• 'Sube volumen', 'Silencio'\n"
            ayuda += "• 'Abre notas y escribe comprar pan'\n\n"
            
            ayuda += "🛠️ DEVOPS (Pro):\n"
            ayuda += "• 'Trabajar en [proyecto]'\n"
            ayuda += "• 'Git status', 'Subir cambios'\n"
            ayuda += "• 'Instalar dependencias', 'Construir'\n"
            ayuda += "• 'Mi IP', 'Libera puerto 8080'\n"
            
            return ayuda, "sara"
		
        # --- COMANDOS DE SISTEMA AVANZADOS ---
        elif any(x in cmd for x in ["limpieza profunda", "limpia sistema", "limpia todo", "limpia temporales y papelera"]):
            return self.sys_control.deep_clean_system(), "sys"
        
        elif "captura pantalla" in cmd or "screenshot" in cmd:
            return self.devops.iniciar_tunel_serveo(), "dev"

        elif "compartir proyecto" in cmd or "serveo" in cmd:
            return self.devops.iniciar_tunel_serveo(), "dev"

        # --- SECCIÓN SISTEMA ---
        # --- SECCIÓN SISTEMA ---
        elif "sistema" in cmd or "estado" in cmd or "monitor" in cmd:
            return self.monitor.obtener_reporte_completo(), "sistema"
        
        # --- ABRIR CONFIGURACIÓN ---
        elif any(x in cmd for x in ["abre configuración", "abre configuracion", "abrir configuración", "abrir configuracion", "abre ajustes", "abrir ajustes", "abre settings", "configuración", "ajustes", "settings"]):
            # Este comando necesita ser manejado por la GUI
            return "OPEN_SETTINGS_TAB", "ui_command"
        
        # --- ABRIR CONFIGURACIÓN DE PERFIL ---
        elif any(x in cmd for x in ["abre mi perfil", "mi perfil", "configurar perfil", "editar perfil", "perfil de usuario", "ver mi perfil", "ver perfil", "mostrar perfil"]):
            return "OPEN_PROFILE_SETTINGS", "ui_command"
        
        # --- MODO SALUD (HEALTH MONITOR) ---
        elif any(x in cmd for x in ["voy a trabajar", "empezar trabajo", "iniciar trabajo", "trabajar en casa", "trabajar en oficina"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            
            # Detectar perfil
            if "casa" in cmd:
                profile = "casa"
            elif "oficina" in cmd:
                profile = "oficina"
            elif "pomodoro" in cmd:
                profile = "pomodoro"
            else:
                profile = "casa"  # Default
            
            return self.health.start_session(profile), "health"
        
        elif any(x in cmd for x in ["pausa trabajo", "pausar trabajo", "descanso"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            return self.health.pause_session(), "health"
        
        elif any(x in cmd for x in ["reanudar trabajo", "continuar trabajo", "volver al trabajo"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            return self.health.resume_session(), "health"
        
        elif any(x in cmd for x in ["terminar trabajo", "fin de jornada", "acabar trabajo"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            return self.health.stop_session(), "health"
        
        elif any(x in cmd for x in ["cuánto tiempo llevo", "cuanto tiempo llevo", "tiempo trabajado"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            return self.health.get_elapsed_time(), "health"
        
        elif any(x in cmd for x in ["próximo descanso", "proximo descanso", "siguiente descanso"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            return self.health.get_next_reminder(), "health"
        
        elif any(x in cmd for x in ["cambiar a modo", "cambiar modo"]):
            if not self.health:
                return "❌ Monitor de salud no disponible", "error"
            
            # Detectar nuevo perfil
            if "casa" in cmd:
                new_profile = "casa"
            elif "oficina" in cmd:
                new_profile = "oficina"
            elif "pomodoro" in cmd:
                new_profile = "pomodoro"
            else:
                return "❌ Especifica el modo: casa, oficina o pomodoro", "error"
            
            return self.health.change_profile(new_profile), "health"
        
        # --- ASISTENTE DE ESTUDIO ---
        elif any(x in cmd for x in ["resume pdf", "resumir pdf", "resumen de pdf"]):
            if not self.study:
                return "❌ Asistente de estudio no disponible", "error"
            
            # Buscar ruta del PDF en el comando
            # Formato: "resume pdf C:\ruta\archivo.pdf"
            match = re.search(r'[A-Za-z]:\\[^\s]+\.pdf', cmd)
            if match:
                pdf_path = match.group(0)
                return self.study.summarize_pdf(pdf_path), "study"
            else:
                return "❌ Especifica la ruta del PDF. Ejemplo: 'resume pdf C:\\Documents\\archivo.pdf'", "error"
        
        elif any(x in cmd for x in ["crea flashcards", "genera flashcards", "flashcards de"]):
            if not self.study:
                return "❌ Asistente de estudio no disponible", "error"
            
            # Extraer tema
            topic = cmd.replace("crea flashcards", "").replace("genera flashcards", "").replace("flashcards de", "").replace("sobre", "").strip()
            
            if not topic:
                return "❌ Especifica el tema. Ejemplo: 'crea flashcards de Python'", "error"
            
            return self.study.generate_flashcards(topic, count=5), "study"
        
        # --- CONTROL DE VIDEOJUEGOS ---
        elif any(x in cmd for x in ["que juegos tengo", "lista juegos", "mis juegos"]):
            if not self.games:
                return "❌ Controlador de juegos no disponible", "error"
            return self.games.list_games(), "games"
        
        elif any(x in cmd for x in ["escanear juegos", "buscar juegos", "detectar juegos"]):
            if not self.games:
                return "❌ Controlador de juegos no disponible", "error"
            return self.games.scan_games(), "games"
        
        elif any(x in cmd for x in ["abre", "juega", "lanza"]) and any(y in cmd for y in ["juego", "valorant", "league", "minecraft", "fortnite", "apex"]):
            if not self.games:
                return "❌ Controlador de juegos no disponible", "error"
            
            # Extraer nombre del juego
            game_name = cmd.replace("abre", "").replace("juega", "").replace("lanza", "").replace("juego", "").strip()
            return self.games.launch_game(game_name), "games"
        
        elif any(x in cmd for x in ["optimiza para jugar", "modo gaming", "modo competitivo", "optimizar juegos"]):
            if not self.games:
                return "❌ Controlador de juegos no disponible", "error"
            return self.games.optimize_for_gaming(), "games"
        
        elif any(x in cmd for x in ["cierra juego", "cerrar juego"]):
            if not self.games:
                return "❌ Controlador de juegos no disponible", "error"
            
            game_name = cmd.replace("cierra juego", "").replace("cerrar juego", "").strip()
            if not game_name:
                return "❌ Especifica qué juego cerrar", "error"
            return self.games.close_game(game_name), "games"
        
        # --- GESTIÓN DE PERFIL DE USUARIO ---
        elif any(x in cmd for x in ["mi perfil", "ver perfil", "mostrar perfil", "configuracion personal"]):
            if not self.perfil:
                return "❌ Perfil no disponible", "error"
            return self.perfil.get_config_summary(), "perfil"
        
        elif any(x in cmd for x in ["llamame", "llámame", "mi nombre es"]):
            if not self.perfil:
                return "❌ Perfil no disponible", "error"
            
            # Extraer nombre
            nombre = cmd.replace("llamame", "").replace("llámame", "").replace("mi nombre es", "").strip()
            if not nombre:
                return "❌ Dime cómo quieres que te llame", "error"
            
            self.perfil.update_user_info(preferred_name=nombre)
            return f"✅ Perfecto, te llamaré {nombre}", "perfil"
        
        elif any(x in cmd for x in ["cambiar idioma", "idioma", "cambiar voz"]):
            if not self.perfil:
                return "❌ Perfil no disponible", "error"
            
            # Detectar idioma
            if "ingles" in cmd or "english" in cmd:
                self.perfil.update_voice_preferences(language="en-US")
                return "✅ Voice language changed to English", "perfil"
            elif "español" in cmd or "espanol" in cmd:
                self.perfil.update_voice_preferences(language="es-ES")
                return "✅ Idioma cambiado a Español", "perfil"
            else:
                return "❌ Idiomas disponibles: Español, Inglés", "error"
        
        elif any(x in cmd for x in ["abre configuracion", "abrir configuracion", "configuracion", "ajustes", "settings"]):
            # Abrir ventana de configuración
            try:
                from config_perfil_ui import abrir_configuracion
                # Nota: Esto abrirá la UI en un thread separado
                import threading
                threading.Thread(target=lambda: abrir_configuracion(None), daemon=True).start()
                return "✅ Abriendo configuración...", "perfil"
            except Exception as e:
                logging.error(f"Error abriendo configuración: {e}")
                return f"❌ Error abriendo configuración: {e}", "error"
        
        # --- MODO ZEN ---
        # Primero verificar SI QUIERE SALIR, porque "salir de modo zen" contiene "modo zen"
        # Ahora acepta también "desactivar modo" o "salir del modo" genérico
        elif (any(x in cmd for x in ["salir", "desactivar", "fin", "quita", "normalidad"]) and any(y in cmd for y in ["zen", "sen", "sem", "cen"])) or \
             any(x in cmd for x in ["desactivar modo", "salir del modo", "quita el modo", "desactiva el modo"]):
            
            # Intentar cerrar la música (busca 'lofi' o 'youtube')
            self.sys_control.close_window_by_title("lofi")
            self.sys_control.close_window_by_title("youtube")
            
            self.sys_control.minimize_all_windows() # Toggle Win+D para restaurar
            return "Modo Zen desactivado. Bienvenid@ de vuelta.", "sistema"

        elif any(x in cmd for x in ["modo zen", "modo sen", "modo sem", "modo cen", "activar zen", "modo relax"]):
            self.sys_control.minimize_all_windows()
            time.sleep(0.5)
            webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk")
            return "Modo Zen Activado. Silenciando notificaciones...", "sistema"

        # --- ORDENAR VENTANAS ---
        elif any(x in cmd for x in ["minimiza el escritorio", "minimiza todo", "minimizar todo", "mostrar escritorio"]):
            return self.sys_control.minimize_all_windows(), "sys"
        
        elif any(x in cmd for x in ["maximiza", "maximizar"]):
            return self.sys_control.maximize_window(), "sys"

        # --- GESTIÓN DE PROCESOS ---
        elif "matar" in cmd or "cerrar" in cmd:
            target = cmd.replace("matar", "").replace("cerrar", "").strip()
            if not target: return "❌ Especifica qué proceso cerrar.", "error"
            # Seguridad: Solo alfanuméricos
            if not re.match(r'^[a-zA-Z0-9_\-\. ]+$', target): return "❌ Nombre inválido.", "error"
            
            return self.sys_control.kill_process(target), "sys"
        
        # --- APAGADO / REINICIO ---
        elif any(x in cmd for x in ["apaga el sistema", "apagar pc", "apaga la computadora"]):
            # Buscar tiempo: "en 10 minutos"
            minutos = 0
            match = re.search(r'en (\d+) minuto', cmd)
            if match: minutos = int(match.group(1))
            
            return self.sys_control.shutdown_system(minutos), "sys"

        elif any(x in cmd for x in ["reinicia", "reiniciar"]):
            minutos = 0
            match = re.search(r'en (\d+) minuto', cmd)
            if match: minutos = int(match.group(1))
            return self.sys_control.restart_system(minutos), "sys"

        elif any(x in cmd for x in ["cancela apagado", "cancelar apagado", "no apagues"]):
            return self.sys_control.cancel_shutdown(), "sys"

        # --- BLOQUEO Y UI ---
        elif "bloquear" in cmd:
            # Usar método del control del sistema si existe, o el clásico
            if hasattr(self.sys_control, 'lock_screen'):
                return self.sys_control.lock_screen(), "sys"
            os.system("rundll32.exe user32.dll,LockWorkStation") # Fallback
            return "PC Bloqueada.", "sistema"
            
        elif any(x in cmd for x in ["vacía la papelera", "limpia la papelera", "vaciar papelera"]):
            return self.sys_control.empty_recycle_bin(), "sys"

        # --- ESTEROIDES DE SISTEMA (NUEVO) ---
        elif any(x in cmd for x in ["toma captura", "toma una captura", "pantallazo", "captura de pantalla"]):
            return self.sys_control.take_screenshot(), "sys"

        elif any(x in cmd for x in ["limpia temporales", "limpieza profunda", "borra basura"]):
            return self.sys_control.clean_temp_files(), "sys"

        elif any(x in cmd for x in ["procesos pesados", "consumo de ram", "qué proceso consume más", "estado de procesos"]):
            return self.sys_control.get_heavy_processes(), "sys"

        # --- MODO OFICIO (Redacción Asistida - REPARADO) ---
        elif any(x in cmd for x in ["redacta oficio", "redactar oficio", "ayuda con oficio", "modo oficio"]):
            # Abrir Word de forma segura
            try:
                # Usar Popen es más seguro que os.system
                subprocess.Popen("start winword", shell=True)
                time.sleep(3) # Tiempo prudente
                # Intentar poner foco y nuevo doc
                pyautogui.press('esc')
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'n')
            except Exception as e:
                logging.error(f"Error abriendo Word: {e}")
                # No retornamos error fatal, seguimos para dar las instrucciones
            
            instrucciones = """📝 MODO OFICIO LISTO

He abierto Word para ti. Ahora dime los detalles así:
"Genera oficio para [Persona] sobre [Asunto] con fecha [Fecha]"

O simplemente di: "Genera el oficio" y te preguntaré los datos.
"""
            return instrucciones, "sys"

        elif "genera el oficio" in cmd or "generar oficio" in cmd or "escribe el oficio" in cmd or "redacta el oficio" in cmd:
            # Verificar IA
            if not self.ia_online:
                return "❌ Necesito conectarme a la IA para redactar. Verifica tu internet o API Key.", "error"
            
            # Limpieza del comando para obtener contexto
            contexto = re.sub(r"(genera|generar|escribe|redacta|el|un|oficio|para|sobre)", "", cmd).strip()
            
            if len(contexto) < 5:
                 return "❌ Dime más detalles. Ej: 'Redacta oficio para Jefe solicitando vacaciones'.", "error"
            
            fecha_hoy = datetime.datetime.now().strftime("%d de %B de %Y")
            
            prompt = f"""Escribe un oficio formal:
            Fecha: {fecha_hoy}
            Detalles: {contexto}.
            
            Estructura: Lugar y Fecha, Destinatario, Asunto, Cuerpo formal, Despedida, Firma.
            Sin explicaciones extra, solo el texto del oficio."""

            respuesta_ia, tipo = self.consultar_ia(prompt)
            
            # Copiar al portapapeles SIEMPRE
            try:
                pyperclip.copy(respuesta_ia)
                msg_extra = "📋 Copiado al portapapeles."
            except:
                msg_extra = "(No pude copiarlo, cópialo tú)"

            return f"✅ Aquí tienes el borrador ({msg_extra}):\n\n{respuesta_ia}", "sys"

        # --- SECCIÓN UTILIDADES ---
        elif "anota" in cmd:
            nota = cmd.replace("anota", "").strip()
            try:
                with open("sara_notas.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.datetime.now()}] {nota}\n")
                return "Nota guardada.", "sistema"
            except: return "Error guardando nota.", "error"

        # Comando rápido "Pon música/algo" -> Asumir YouTube
        elif "pon" in cmd or "reproduce" in cmd:
            # Limpieza mejorada de palabras basura
            objetivo = re.sub(r"(pon|reproduce|el|la|los|las|un|una|de|por favor|eh|ver|escuchar)", "", cmd).strip()
            
            try:
                if pywhatkit:
                    pywhatkit.playonyt(objetivo)
                    return f"✅ Reproduciendo '{objetivo}'...", "sara"
                else:
                    # Fallback si falla la librería
                    import urllib.parse
                    query = urllib.parse.quote(objetivo)
                    url = f"https://www.youtube.com/results?search_query={query}"
                    webbrowser.open(url)
                    return f"✅ Buscando '{objetivo}' en YouTube...", "sara"
            except Exception as e:
                return f"❌ Error al reproducir: {e}", "error"

        elif any(x in cmd for x in ["abre", "abrir", "busca"]):
            objetivo = re.sub(r"(abre|abrir|busca|buscar|el|la|por favor)", "", cmd).strip()
            return self.abrir_inteligente(objetivo, cmd)

        # --- CRONOS (ALARMAS INTELIGENTES) ---
        elif any(x in cmd for x in ["recuérdame", "recuerdame", "despiértame", "despiertame", "alarma", "avísame"]):
            # 1. Intento: Tiempo relativo ("en X minutos")
            match_tiempo = re.search(r'(en|dentro de)\s+(\d+)\s+(minuto|hora|segundo)', cmd)
            
            # 2. Intento: Tiempo absoluto ("a las 6:00 pm")
            match_hora = re.search(r'a las\s+(\d{1,2})(:(\d{2}))?\s*(am|pm)?', cmd)
            
            # Determinar mensaje
            mensaje = "Recordatorio"
            if "despi" in cmd: mensaje = "¡Despertar!"
            elif "recuérdame" in cmd or "recuerdame" in cmd:
                if " que " in cmd: mensaje = cmd.split(" que ")[1].strip()
                elif " avísame " in cmd: pass
                # Clean simple
                mensaje = mensaje.replace("mañana", "").replace("a las", "").strip()

            if match_tiempo:
                cantidad = int(match_tiempo.group(2))
                unidad = match_tiempo.group(3)
                minutos = cantidad
                if "hora" in unidad: minutos = cantidad * 60
                elif "segundo" in unidad: minutos = cantidad / 60
                return self.cronos.programar_alarma(minutos, mensaje), "sys"
                
            elif match_hora:
                try:
                    hora = int(match_hora.group(1))
                    minutos = int(match_hora.group(3)) if match_hora.group(3) else 0
                    periodo = match_hora.group(4) # am/pm
                    
                    if periodo:
                        if periodo == "pm" and hora < 12: hora += 12
                        elif periodo == "am" and hora == 12: hora = 0
                        
                    now = datetime.datetime.now()
                    target = now.replace(hour=hora, minute=minutos, second=0, microsecond=0)
                    
                    # Si ya pasó la hora hoy, o si dice "mañana", sumar un día
                    if target < now or "mañana" in cmd:
                        target += datetime.timedelta(days=1)
                        
                    return self.cronos.programar_alarma_dt(target, mensaje), "sys"
                except Exception as e:
                    return f"❌ Error interpretando hora: {e}", "error"

            else:
                return "❌ Dime la hora. Ejemplo: 'En 5 minutos' o 'A las 7:00 am'.", "error"

        # --- POMODORO (PRODUCTIVIDAD) ---
        elif self.pomodoro and any(x in cmd for x in ["pomodoro", "concentración", "concentracion", "enfoque"]):
            # Iniciar Pomodoro
            if any(x in cmd for x in ["inicia", "iniciar", "empieza", "empezar", "comienza", "comenzar"]):
                # Duración personalizada
                match_duracion = re.search(r'(\d+)\s*(minuto|min)', cmd)
                if match_duracion:
                    duracion = int(match_duracion.group(1))
                    return self.pomodoro.start_work_session(duracion), "sys"
                else:
                    return self.pomodoro.start_work_session(), "sys"
            
            # Pausar
            elif any(x in cmd for x in ["pausa", "pausar", "detén", "deten"]):
                return self.pomodoro.pause(), "sys"
            
            # Reanudar
            elif any(x in cmd for x in ["reanuda", "reanudar", "continúa", "continua", "sigue"]):
                return self.pomodoro.resume(), "sys"
            
            # Terminar/Detener
            elif any(x in cmd for x in ["termina", "terminar", "detener", "cancela", "cancelar", "para"]):
                return self.pomodoro.stop(), "sys"
            
            # Estadísticas
            elif any(x in cmd for x in ["estadística", "estadistica", "reporte", "resumen"]):
                return self.pomodoro.get_statistics(), "sys"
            
            # Configurar
            elif "configura" in cmd or "configurar" in cmd:
                # Buscar patrón: "configura pomodoro 30 minutos"
                match_config = re.search(r'(\d+)\s*minuto', cmd)
                if match_config:
                    work_min = int(match_config.group(1))
                    return self.pomodoro.configure(work_minutes=work_min), "sys"
                else:
                    return "❌ Ejemplo: 'Configura pomodoro 30 minutos'", "error"
            
            # Estado actual
            elif "estado" in cmd or "cuánto" in cmd or "cuanto" in cmd:
                status = self.pomodoro.get_status()
                if status['is_running']:
                    tipo = "trabajo" if status['session_type'] == 'work' else "descanso"
                    estado_pausa = " (pausado)" if status['is_paused'] else ""
                    return f"⏱️ Pomodoro en {tipo}{estado_pausa}: {status['time_remaining_formatted']} restantes", "sys"
                else:
                    return f"⏱️ No hay sesión activa. Pomodoros hoy: {status['pomodoros_today']}", "sys"
            
            # Descanso
            elif "descanso" in cmd:
                largo = "largo" in cmd
                return self.pomodoro.start_break(long_break=largo), "sys"
            
            else:
                # Ayuda de Pomodoro
                ayuda_pomo = """⏱️ COMANDOS POMODORO:
• "Inicia pomodoro" - 25 min de trabajo
• "Inicia pomodoro 30 minutos" - Personalizado
• "Pausa pomodoro" - Pausar sesión
• "Reanuda pomodoro" - Continuar
• "Termina pomodoro" - Detener
• "Estado de pomodoro" - Ver tiempo restante
• "Estadísticas de pomodoro" - Ver resumen
• "Descanso corto/largo" - Iniciar descanso
"""
                return ayuda_pomo, "sys"

        # --- ORGANIZADOR INTELIGENTE ---
        elif any(x in cmd for x in ["ordena", "ordenar", "limpia", "limpiar", "organiza"]):
            if "escritorio" in cmd: target = "escritorio"
            elif "descargas" in cmd: target = "descargas"
            elif "documentos" in cmd: target = "documentos"
            else: return "❌ ¿Qué carpeta ordeno? (Escritorio, Descargas, Documentos)", "error"
            
            return SystemOps.organizar_archivos(target), "sys"

        # --- SARA VISION (OJOS) ---
        elif any(x in cmd for x in ["mira mi pantalla", "mira la pantalla", "qué ves", "que ves", "analiza esto", "analiza la pantalla"]):
            return self.ver_pantalla(cmd), "ai"

        # --- CODE REVIEW CON IA ---
        elif self.code_reviewer and any(x in cmd for x in ["revisa", "analiza código", "analiza codigo", "code review"]):
            # Extraer nombre de archivo
            archivo = None
            
            # Buscar patrón "revisa brain.py" o "analiza brain.py"
            match_archivo = re.search(r'(revisa|analiza|review)\s+(\w+\.py)', cmd)
            if match_archivo:
                archivo = match_archivo.group(2)
            
            # Si no especificó archivo, pedir uno
            if not archivo:
                return "❌ Especifica el archivo. Ejemplo: 'Revisa brain.py'", "error"
            
            # Construir ruta completa
            ruta = os.path.join(DevOpsManager.WORK_DIR, archivo)
            
            # Determinar tipo de análisis
            if "seguridad" in cmd or "security" in cmd:
                tipo = "security"
            elif "rendimiento" in cmd or "performance" in cmd:
                tipo = "performance"
            elif "profundo" in cmd or "deep" in cmd:
                tipo = "deep"
            else:
                tipo = "quick"
            
            return self.code_reviewer.analizar_archivo(ruta, tipo)
        
        # Generar tests
        elif self.code_reviewer and any(x in cmd for x in ["genera tests", "generar tests", "crear tests"]):
            match_archivo = re.search(r'(para|de)\s+(\w+\.py)', cmd)
            if match_archivo:
                archivo = match_archivo.group(2)
                ruta = os.path.join(DevOpsManager.WORK_DIR, archivo)
                return self.code_reviewer.generar_tests(ruta)
            else:
                return "❌ Especifica el archivo. Ejemplo: 'Genera tests para brain.py'", "error"
        
        # Generar documentación
        elif self.code_reviewer and any(x in cmd for x in ["documenta", "documentar", "genera documentación", "genera documentacion"]):
            match_archivo = re.search(r'(documenta|documentar)\s+(\w+\.py)', cmd)
            if not match_archivo:
                match_archivo = re.search(r'(para|de)\s+(\w+\.py)', cmd)
            
            if match_archivo:
                archivo = match_archivo.group(2)
                ruta = os.path.join(DevOpsManager.WORK_DIR, archivo)
                return self.code_reviewer.generar_documentacion(ruta)
            else:
                return "❌ Especifica el archivo. Ejemplo: 'Documenta brain.py'", "error"
        
        # Sugerir refactoring
        elif self.code_reviewer and any(x in cmd for x in ["refactoriza", "refactorizar", "mejora código", "mejora codigo"]):
            match_archivo = re.search(r'(\w+\.py)', cmd)
            if match_archivo:
                archivo = match_archivo.group(1)
                ruta = os.path.join(DevOpsManager.WORK_DIR, archivo)
                return self.code_reviewer.sugerir_refactoring(ruta)
            else:
                return "❌ Especifica el archivo. Ejemplo: 'Refactoriza brain.py'", "error"
        
        # Explicar código
        elif self.code_reviewer and any(x in cmd for x in ["explica", "explicar código", "explicar codigo", "qué hace", "que hace"]):
            match_archivo = re.search(r'(\w+\.py)', cmd)
            if match_archivo:
                archivo = match_archivo.group(1)
                ruta = os.path.join(DevOpsManager.WORK_DIR, archivo)
                return self.code_reviewer.explicar_codigo(ruta)
            else:
                return "❌ Especifica el archivo. Ejemplo: 'Explica brain.py'", "error"

        # --- MODO CENTINELA (SEGURIDAD) ---
        elif "centinela" in cmd or "sistema de seguridad" in cmd:
            # DESACTIVAR tiene prioridad (si dice desactiva/quita/apaga)
            if any(x in cmd for x in ["desactiva", "quita", "apaga", "salir", "detener"]):
                 return "🔓 Contraseña aceptada. Centinela desactivado.", "sentinel_off"
            # ACTIVAR (Por defecto si solo menciona "centinela")
            else:
                 return "🛡️ CENTINELA ACTIVADO. Sistema bloqueado.", "sentinel_on"
                 
        elif "codigo alfa" in cmd or "código alfa" in cmd:
             return "🔓 Contraseña aceptada. Centinela desactivado.", "sentinel_off"

        # --- (SECCIÓN ELIMINADA: LEGACY FACIAL RECOGNITION) ---
        # El reconocimiento facial ahora es manejado por NetworkGuardian o eliminado según solicitud.

        # --- CONTROL DE VOLUMEN (FALLBACK LOCAL) ---
        # --- CONTROL DE VOLUMEN (FALLBACK LOCAL) ---
        # --- CONTROL DE VOLUMEN (FALLBACK LOCAL) ---
        elif any(x in cmd for x in ["volumen", "sonido", "audio", "subele", "bajale", "súbele", "bájale"]):
            try:
                # 1. Prioridad: Definir Nivel Específico (ej: "a 20", "al 50", "baja a 10")
                numeros = [int(s) for s in cmd.split() if s.isdigit()]
                if numeros:
                    # Si hay un número, asumimos que es el objetivo absoluto
                    # Esto arregla "baja a 20" ejecutándose como "baja" (-10)
                    return self.sys_control.set_volume(numeros[0]), "sys"
                
                # 2. Ajustes Relativos
                if any(x in cmd for x in ["sube", "subir", "súbele", "subele"]):
                    return self.sys_control.adjust_volume(10), "sys"
                elif any(x in cmd for x in ["baja", "bajar", "bájale", "bajale"]):
                    return self.sys_control.adjust_volume(-10), "sys"
                
                # Evitar eco: Si la frase es "volumen ajustado" (lo que dice SARA), ignorar
                if "ajustado" in cmd or "activo" in cmd:
                    return "", "none"
                    
                return "🔊 Control de volumen activo. Di 'sube', 'baja' o 'volumen al 50'.", "sys"
            except Exception as e:
                return f"❌ Error volumen: {e}", "error"

        # --- AYUDA / COMANDOS ---
        elif any(x in cmd for x in ["ayuda", "comandos", "qué puedes hacer", "que puedes hacer"]):
            ayuda = """📋 TODOS LOS COMANDOS DE SARA:

🎵 MEDIA & ENTRETENIMIENTO:
• "Pon/Reproduce [canción/video]" - YouTube automático
• "Abre YouTube/Spotify/Netflix"
• "Sube/Baja volumen" - Control de audio
• "Silencio/Mute/Pausa" - Control multimedia
• "Modo Zen" - Música relajante + escritorio limpio

🛡️ SEGURIDAD (CENTINELA):
• "Modo Centinela" - Bloqueo pantalla total
• "Activa Centinela" - Bloqueo pantalla
• "Desactiva Centinela" - Desbloqueo
• "Código Alfa" - Desbloqueo de emergencia
• "Bloquear" - Bloqueo de Windows

⏰ CRONOS (Alarmas Inteligentes):
• "Despiértame en [X] minutos/horas"
• "Recuérdame [mensaje] en [X] minutos"
• "Alarma mañana a las 7:00 AM"
• "Avísame en 30 minutos"

📁 ORGANIZADOR INTELIGENTE:
• "Ordena escritorio" - Organiza por tipo
• "Limpia descargas" - Categoriza archivos
• "Organiza documentos" - Mueve a carpetas

🌐 NETWORK GUARDIAN:
• "Escanea red/wifi" - Ver dispositivos
• "Dispositivos conectados" - Lista completa
• "Investiga dispositivo [IP]" - Info detallada
• "Bloquea dispositivo [IP]" - Expulsar intruso
• "Desbloquea dispositivo [IP]" - Restaurar acceso

👁️ SARA VISION (Gemini):
• "Mira mi pantalla" - Analiza lo que ves
• "Qué ves" - Describe la pantalla
• "Analiza esto" - Interpreta contenido

🔧 CONTROL DE SISTEMA:
• "Sistema/Estado/Monitor" - Reporte completo
• "Abre [programa]" - Ejecuta apps
• "Matar/Cerrar [proceso]" - Termina tareas
• "Mi IP" - Muestra IP local
• "Libera puerto [número]" - Limpia puerto
• "Fecha" - Día actual
• "Volumen [0-100]" - Nivel exacto

📝 PRODUCTIVIDAD:
• "Modo Dictado" - Escribe por ti
• "Anota [texto]" - Guarda notas
• "Traduce" - Traduce portapapeles
• "Abre notas y escribe [X]" - Nota rápida

🛠️ DEVOPS (Desarrolladores):
• "Trabajar en [carpeta]" - Cambia directorio
• "Git status" - Estado del repo
• "Subir cambios" - Git push
• "Instalar dependencias" - npm/pip install
• "Construir" - Build del proyecto
• "Compartir proyecto" - Túnel público

💬 IA CONVERSACIONAL:
• Pregunta lo que quieras
• Explica código, conceptos
• Genera ideas, resuelve problemas
• Asistencia general

🎮 COMANDOS DIRECTOS (Sin "SARA"):
• Pon/Reproduce [X]
• Silencio/Pausa/Mute
• Ordena/Limpia [carpeta]
• Modo Centinela
• Desactiva Centinela
• Código Alfa
"""
            return ayuda, "sys"



        elif "traduce" in cmd:
            try:
                txt = pyperclip.paste()
                if not txt: return "Portapapeles vacío.", "error"
                return self.consultar_ia(f"Traduce al español:\n{txt[:MAX_CHARS_TRANSLATION]}"), "ai"
            except: return "Error en traducción.", "error"

        elif "hora" in cmd: 
            now = datetime.datetime.now()
            hora = now.hour
            minutos = now.minute
            
            # Convertir a 12 horas
            periodo = "de la mañana" if hora < 12 else "de la tarde" if hora < 19 else "de la noche"
            if hora > 12:
                hora -= 12
            elif hora == 0:
                hora = 12
                
            # Formato natural para voz
            if minutos == 0:
                tiempo_texto = f"Son las {hora} {periodo}"
            else:
                tiempo_texto = f"Son las {hora} y {minutos} {periodo}"
                
            return tiempo_texto, "sistema"
        elif "fecha" in cmd: 
            return f"Hoy es {datetime.datetime.now().strftime('%A %d de %B')}", "sistema"

        
        # Escaneo de red WiFi
        elif any(x in cmd for x in ["escanea red", "escanea wifi", "escanea mi red", "escanear red", "escanear wifi", "dispositivos conectados", "cuantos dispositivos", "ver dispositivos"]):
            resultado = self.monitor.escanear_red()
            
            if 'error' in resultado:
                return f"❌ No pude escanear la red: {resultado['error']}", "error"
            
            total = resultado['total']
            dispositivos = resultado['dispositivos']
            ip_local = resultado.get('ip_local', 'Desconocida')
            
            if total == 0:
                return "No encontré dispositivos conectados. Asegúrate de estar conectado a WiFi.", "sara"
            
            respuesta = f"🌐 Encontré {total} dispositivos en tu red (IP: {ip_local}):\n\n"
            
            # Mostrar hasta 10 dispositivos
            for i, disp in enumerate(dispositivos[:10], 1):
                tipo = disp['tipo']
                ip = disp['ip']
                respuesta += f"{i}. {tipo} - {ip}\n"
            
            if total > 10:
                respuesta += f"\n... y {total - 10} dispositivos más."
            
            return respuesta, "sara"
        
        # Investigar dispositivo específico
        elif any(x in cmd for x in ["investiga el dispositivo", "investiga dispositivo", "información del dispositivo", "info del dispositivo"]):
            # Extraer IP del comando
            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', cmd)
            
            if not ip_match:
                return "❌ No encontré una IP válida. Ejemplo: 'investiga el dispositivo 192.168.1.105'", "error"
            
            ip = ip_match.group(0)
            info = self.monitor.investigar_dispositivo(ip)
            
            respuesta = f"🔍 Investigación del dispositivo {ip}:\n\n"
            respuesta += f"Estado: {'🟢 Activo' if info['activo'] else '🔴 Inactivo'}\n"
            
            if info['activo']:
                respuesta += f"Latencia: {info['latencia']}\n"
                respuesta += f"Nombre: {info['hostname']}\n"
                respuesta += f"OS Probable: {info['os_probable']}\n"
                
                if info['puertos_abiertos']:
                    respuesta += f"\nPuertos abiertos:\n"
                    for puerto in info['puertos_abiertos']:
                        respuesta += f"  • {puerto}\n"
                else:
                    respuesta += "\nNo se detectaron puertos abiertos comunes."
            else:
                respuesta += "\nEl dispositivo no responde al ping."
            
            return respuesta, "sara"
        
        # Bloquear dispositivo
        elif any(x in cmd for x in ["bloquea el dispositivo", "bloquea dispositivo", "bloquear dispositivo", "echa al dispositivo"]):
            # Extraer IP
            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', cmd)
            
            if not ip_match:
                return "❌ No encontré una IP válida. Ejemplo: 'bloquea el dispositivo 192.168.1.105'", "error"
            
            ip = ip_match.group(0)
            resultado = self.monitor.bloquear_ip_local(ip)
            
            return resultado['mensaje'], "sara" if resultado['exito'] else "error"
        
        # Desbloquear dispositivo
        elif any(x in cmd for x in ["desbloquea el dispositivo", "desbloquea dispositivo", "desbloquear dispositivo"]):
            # Extraer IP
            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', cmd)
            
            if not ip_match:
                return "❌ No encontré una IP válida. Ejemplo: 'desbloquea el dispositivo 192.168.1.105'", "error"
            
            ip = ip_match.group(0)
            resultado = self.monitor.desbloquear_ip_local(ip)
            
            return resultado['mensaje'], "sara" if resultado['exito'] else "error"
        
        elif "configura" in cmd:
            return "📝 Ve a la pestaña 'Configuración' para agregar tus API Keys.", "sys"

        # --- ADVANCED PC CONTROL (IRON MAN MODE) ---
        
        # 1. Control de Dictado
        if "modo dictado" in cmd or "toma dictado" in cmd:
            self.dictation_mode = True
            return "📝 Modo Dictado ACTIVADO. Di 'terminar dictado' para finalizar.", "sara"
        
        # 2. Control Multimedia
        # 2. Control Multimedia
        elif "sube volumen" in cmd:
            return self.sys_control.adjust_volume(10), "sys"
        elif "baja volumen" in cmd:
            return self.sys_control.adjust_volume(-10), "sys"
        elif "silencio" in cmd or "mute" in cmd:
            pyautogui.press("volumemute")
            return "🔇 Silencio.", "local"
        elif "pausa" in cmd or "play" in cmd or "continuar" in cmd:
            pyautogui.press("playpause")
            return "⏯️ Play/Pausa.", "local"

        # 3. Macro: Abre App y Escribe
        # Ej: "Abre notas y escribe comprar leche"
        elif "abre" in cmd and "y escribe" in cmd:
            try:
                # Parsear: "abre [app] y escribe [texto]"
                parte_app = re.search(r"abre (.*?) y escribe", cmd).group(1).strip()
                parte_texto = cmd.split("y escribe")[1].strip()
                
                # 1. Abrir App
                resp_abrir = self.abrir_inteligente(parte_app, cmd)
                if "Error" in resp_abrir or "No pude" in resp_abrir:
                    return resp_abrir, "error"
                
                # 2. Esperar (necesario para que la ventana tenga el foco)
                time.sleep(2.0)
                
                # 3. Escribir
                pyautogui.write(parte_texto, interval=0.05)
                return f"✅ Tarea completada en {parte_app}.", "sara"
            except Exception as e:
                return f"❌ Error en macro: {e}", "error"

        # 4. Macro: Abre App y Reproduce/Busca (NUEVO)
        # Ej: "Abre YouTube y reproduce rock"
        elif "abre" in cmd and ("y reproduce" in cmd or "y busca" in cmd):
            try:
                separador = "y reproduce" if "y reproduce" in cmd else "y busca"
                parte_app = re.search(f"abre (.*?) {separador}", cmd).group(1).strip()
                parte_texto = cmd.split(separador)[1].strip()
                
                # Detectar si es YouTube para búsqueda directa (más rápido)
                if "youtube" in parte_app.lower() or "you tube" in parte_app.lower():
                    import urllib.parse
                    query = urllib.parse.quote(parte_texto)
                    url = f"https://www.youtube.com/results?search_query={query}"
                    webbrowser.open(url)
                    return f"✅ Buscando '{parte_texto}' en YouTube...", "sara"
                
                # Para otras apps, usar método clásico
                resp_abrir = self.abrir_inteligente(parte_app, cmd)
                if "Error" in resp_abrir or "No pude" in resp_abrir:
                    return resp_abrir, "error"
                
                time.sleep(4.0)
                pyautogui.write(parte_texto, interval=0.05)
                time.sleep(0.5)
                pyautogui.press("enter")
                
                return f"✅ Buscando '{parte_texto}' en {parte_app}...", "sara"
            except Exception as e:
                return f"❌ Error en macro multimedia: {e}", "error"

        # --- OPTIMIZACIÓN HÍBRIDA (NUEVO) ---
        
        # 1. Charlas Locales Avanzadas (Ahorro de Tokens + Personalidad)
        import random
        
        # --- NUEVO: COMANDO DE CIERRE REAL ---
        if any(x in cmd for x in ["ciérrate", "cierra el programa", "cierra s.a.r.a", "apágate", "nos vemos"]):
            return "¡Hasta luego! Cerrando sistemas...", "exit"
        
        # Patrones (Regex) -> [Posibles Respuestas]
        REGLAS_CHAT_LOCAL = [
            (r"(hola|buenas|holis|que tal).*", [
                "¡Hola! Lista para programar.", 
                "¡Buenas! ¿Qué rompimos hoy? 😉", 
                "Hola. Sistemas nominales y esperando órdenes.",
                "¡Hey! ¿Café y código?"
            ]),
            (r".*(gracias|agradecido).*", [
                "¡De nada! Para eso estoy.",
                "Un placer.",
                "No hay de qué. ¿Seguimos?",
                "Siempre operativa para ti."
            ]),
            (r".*(quien eres|que eres).*", [
                "Soy SARA (Sistema Avanzado de Respuesta y Asistencia). Tu copiloto.",
                "Una IA diseñada para hacerte la vida más fácil (y compilar tu código).",
                "Soy tu asistente de desarrollo. Tú pones la lógica, yo pongo los comandos."
            ]),
            (r".*(adios|chao|hasta luego|bye).*", [
                "Hasta luego. Mantendré el fuerte mientras no estás.",
                "Nos vemos. No olvides hacer commit.",
                "Chao. Pasando a modo reposo (pero vigilando)."
            ]),
            (r".*(buenos dias).*", ["¡Buenos días! Espero que hayas dormido bien. ¿Le damos al código?", "Buenos días. ¿Café listo?"]),
            (r".*(buenas noches).*", ["Buenas noches. Descansa, yo me encargo de los logs.", "Hasta mañana. Sueña con ovejas eléctricas."]),
            (r".*(como estas|que haces).*", ["Operativa y al 100%.", "Analizando el entorno. Todo en verde.", "Esperando tu próximo gran comando."]),
            (r".*(eres real).*", ["Tan real como tu código (esperemos que con menos bugs 😉).", "Pienso, luego existo... en tu RAM."])
        ]
        
        # Comando de hora (con formato legible para voz)
        if any(x in cmd for x in ["qué hora", "que hora", "hora es", "dime la hora"]):
            ahora = datetime.datetime.now()
            hora = ahora.hour
            minutos = ahora.minute
            
            # Convertir a formato 12 horas
            if hora == 0:
                hora_12 = 12
                periodo = "de la madrugada"
            elif hora < 12:
                hora_12 = hora
                periodo = "de la mañana"
            elif hora == 12:
                hora_12 = 12
                periodo = "del mediodía"
            else:
                hora_12 = hora - 12
                periodo = "de la tarde" if hora < 20 else "de la noche"
            
            # Formato natural para voz
            if minutos == 0:
                return f"Son las {hora_12} en punto {periodo}", "sara"
            else:
                return f"Son las {hora_12} con {minutos} minutos {periodo}", "sara"
        
        # --- RESPUESTAS INTELIGENTES SIN IA (KNOWLEDGE BASE) ---
        # SARA es consciente de sus propias capacidades
        smart_response = SaraKnowledge.smart_response(cmd)
        if smart_response:
            return smart_response, "sara"
        
        for patron, respuestas in REGLAS_CHAT_LOCAL:
            if re.search(patron, cmd):
                return random.choice(respuestas), "sara"

        # 2. Calculadora Local (Evitar IA para matemáticas simples)
        # Patrones: "cuanto es 5+5", "calcula 2*3"
        if "cuanto es" in cmd or "calcula" in cmd:
            try:
                # Extraer expresión matemática
                expr = cmd.replace("cuanto es", "").replace("calcula", "").replace("x", "*").strip()
                # Filtrar caracteres peligrosos (solo permitir números y operadores)
                if re.match(r'^[\d\+\-\*\/\.\(\)\s]+$', expr):
                    resultado = eval(expr) # Seguro porque filtramos con regex estricto
                    respuesta = f"🧮 Resultado: {resultado}"
                    # Guardar en memoria
                    if self.memory:
                        self.memory.add_turn(comando, respuesta, intent="math")
                    return respuesta, "sara"
            except: pass

        # --- IA ROUTER (INTELIGENTE) ---
        # Si no se encontró comando directo, usar IA para interpretar y ejecutar
        else:
            if not self.ia_online:
                return "💡 Comandos: 'sistema', 'trabajar en [ruta]', 'git status'. Configura la IA para más.", "sys"
            
            # Agregar contexto si existe
            comando_con_contexto = comando
            if contexto_adicional:
                comando_con_contexto = f"{contexto_adicional}\nUsuario: {comando}"
            
            # Usar IA para interpretar el comando y decidir qué hacer
            respuesta, origen = self._ai_command_router(comando_con_contexto)
            
            # Guardar en memoria
            if self.memory:
                self.memory.add_turn(comando, respuesta, intent="ai")
            
            return respuesta, origen
    
    def _ai_command_router(self, comando: str):
        """
        Router inteligente que usa IA para interpretar comandos ambiguos
        y ejecutarlos automáticamente
        """
        # Contexto para la IA sobre las capacidades de SARA
        system_prompt = f"""Eres SARA, un asistente de voz inteligente. 

Tu trabajo es interpretar el comando del usuario y EJECUTARLO automáticamente.

CAPACIDADES DISPONIBLES:
1. ESTUDIO: Resumir PDFs, crear flashcards
2. GAMING: Abrir juegos, optimizar sistema
3. SALUD: Iniciar/pausar trabajo, ver tiempo trabajado
4. SISTEMA: Limpieza, volumen, procesos, apagar
5. PRODUCTIVIDAD: Modo Zen, Pomodoro
6. DEVOPS: Git commands
7. TIEMPO: Hora, fecha

INSTRUCCIONES:
- Si el usuario pide abrir un juego → responde: "EJECUTAR: abre [nombre del juego]"
- Si pide limpiar → responde: "EJECUTAR: limpieza profunda"
- Si pide trabajar → responde: "EJECUTAR: voy a trabajar"
- Si pide optimizar → responde: "EJECUTAR: modo competitivo"
- Si es una pregunta general → responde normalmente

Comando del usuario: "{comando}"

¿Qué debo hacer?"""

        try:
            # Consultar IA
            respuesta_ia, _ = self.consultar_ia(system_prompt, "")
            
            # Si la IA dice "EJECUTAR:", extraer el comando y ejecutarlo
            if "EJECUTAR:" in respuesta_ia:
                # Extraer comando después de "EJECUTAR:"
                comando_ejecutar = respuesta_ia.split("EJECUTAR:")[1].strip()
                logging.info(f"🤖 AI Router ejecutando: {comando_ejecutar}")
                
                # Ejecutar el comando interpretado recursivamente
                return self.procesar(comando_ejecutar)
            else:
                # Respuesta normal de la IA
                return respuesta_ia, "ia"
                
        except Exception as e:
            logging.error(f"Error en AI Router: {e}")
            # Fallback a respuesta normal
            contexto = f"\n\nDirectorio actual de trabajo: {DevOpsManager.WORK_DIR}. Ayuda con comandos Git si se solicita."
            return self.consultar_ia(comando, contexto)

