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
import asyncio
import platform

# Fix para 'Event loop is closed' en Windows con aiohttp
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
from calendar_module import SaraCalendar
from conversation_memory import ConversationMemory
from weather_api import obtener_weather
from routines import obtener_rutinas  # NUEVO  # NUEVO
from second_brain import SecondBrain # CEREBRO VECTORIAL (NUEVO)
from intent_classifier import HybridIntentClassifier # NLU HÍBRIDO (NUEVO)
from web_agent import SaraWebSurfer # AGENTE WEB (NUEVO)
from gesture_controller import crear_gesture_controller # CONTROL DE GESTOS (NUEVO)

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
        self.monitor = SystemMonitor()
        self.kv_memory = MemoryManager() # RENOMBREADO: Cerebro a largo plazo (Key-Value)
        self.cronos = CronosManager(self)
        
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
            self.calendar = SaraCalendar()
            logging.info("✅ SaraCalendar inicializado")
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
            logging.info(f"✅ WeatherAPI inicializada ({self.weather.default_city})")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando WeatherAPI: {e}")
            self.weather = None
        
        # Inicializar Rutinas (NUEVO)
        try:
            self.routines = obtener_rutinas(self)
            logging.info("✅ RoutineManager inicializado")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando RoutineManager: {e}")
            self.routines = None
        
        # Inicializar Gesture Controller (NUEVO)
        try:
            self.gesture_controller = crear_gesture_controller(
                brain_ref=self,
                callback=self.voz.hablar,
                show_camera=False  # Sin ventana por defecto
            )
            logging.info("✅ GestureController inicializado (inactivo)")
        except Exception as e:
            logging.error(f"⚠️ Error inicializando GestureController: {e}")
            self.gesture_controller = None
        self._gesture_controller_loaded = False
            
        self.conectar_ias()
        self.dictation_mode = False
        
        # Asignar callback de IA al intent classifier (después de conectar_ias)
        # Asignar callback de IA al intent classifier (después de conectar_ias)
        if self.intent_classifier:
            self.intent_classifier.ia_callback = self.consultar_ia

        # MAPA DE COMANDOS (Command Pattern) - INICIALIZACIÓN DE HANDLERS
        self._init_command_handlers()

    def _init_command_handlers(self):
        """Registra los manejadores para cada intención"""
        self.handlers = {
            "MEMORIZAR": self._handle_second_brain_memorize,
            "VOLUMEN_SUBIR": self._handle_volume_up,
            "VOLUMEN_BAJAR": self._handle_volume_down,
            "SILENCIO": self._handle_volume_mute,
            "ABRIR_APP": self._handle_open_app,
            "BUSCAR_WEB": self._handle_web_search,
            "LEER_DOCUMENTO": self._handle_read_doc,
            "REPRODUCIR_MEDIA": self._handle_media,
            "ALARMA": self._handle_alarm,
            "CLIMA": self._handle_weather,
            "MODO_ESTUDIO": self._handle_study_mode,
            "STUDY_RESUME_PDF": self._handle_study_resume,
            "STUDY_FLASHCARDS": self._handle_study_flashcards,
            "HORA_FECHA": self._handle_time_date,
            "TRADUCIR": self._handle_translate,
            "CALCULAR": self._handle_calculate,
            "MODO_ZEN": self._handle_zen_mode,
            "CONTROL_GESTOS": self._handle_gestures,
            "DIAGNOSTICO_RED": self._handle_network_diag,
            "SENTINEL_ACTIVAR": self._handle_sentinel_on,
            "SENTINEL_DESACTIVAR": self._handle_sentinel_off,
            "CONFIGURACION": self._handle_ui_config,
            "PERFIL": self._handle_ui_profile,
            "GIT_STATUS": lambda p, s: (self.devops.git_status(), "dev") if self.devops else ("Error devops", "error"),
            "GIT_PUSH": lambda p, s: (self.devops.git_smart_push("Update SARA"), "dev") if self.devops else ("Error devops", "error"),
            "GIT_PULL": lambda p, s: (self.devops.git_pull(), "dev") if self.devops else ("Error devops", "error")
        }

    # --- HANDLERS ESPECÍFICOS ---
    def _handle_second_brain_memorize(self, params, source):
        if self.second_brain:
            res = self.second_brain.memorizar(params.get("data", ""))
            return f"✅ {res}", "sara"
        return "Cerebro desconectado.", "error"

    def _handle_volume_up(self, params, source):
        if self.sys_control:
            return self.sys_control.adjust_volume(params.get("amount", 10)), "sys"
        return "Control de sistema no disponible", "error"

    def _handle_volume_down(self, params, source):
        if self.sys_control:
            return self.sys_control.adjust_volume(-params.get("amount", 10)), "sys"
        return "Control de sistema no disponible", "error"

    def _handle_volume_mute(self, params, source):
        if self.sys_control: return self.sys_control.mute_volume(), "sys"
        return "Error sys", "error"

    def _handle_open_app(self, params, source):
        return self.abrir_inteligente(params.get("app_name", ""), "cmd")
    
    def _handle_web_search(self, params, source):
        if self.web_agent:
            query = params.get("query", "")
            res = self.web_agent.buscar_google(query)
            if self.ia_online:
                resumen, _ = self.consultar_ia(f"Resume: {res}")
                return resumen, "sara"
            return f"🔎 {res}", "sara"
        return "Web Agent offline", "error"

    def _handle_read_doc(self, params, source):
        if self.web_agent:
            url = pyperclip.paste().strip()
            if "http" in url:
                contenido = self.web_agent.leer_pagina(url)
                if self.ia_online:
                    resumen, _ = self.consultar_ia(f"Resume: {contenido}")
                    return resumen, "sara"
                return contenido[:500], "sara"
        return "No hay agente web", "error"

    def _handle_media(self, params, source):
        query = params.get("query", "")
        if query:
            import webbrowser
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"🎵 Reproduciendo {query}", "media"
        return "Acción multimedia", "media"

    def _handle_alarm(self, params, source):
        if self.cronos:
            return self.cronos.programar_alarma(params.get("minutes", 5), params.get("message", "Alarma")), "sara"
        return "Cronos offline", "error"
        
    def _handle_weather(self, params, source):
        if self.weather:
            city = params.get("city")
            # Weather handler necesita ser síncrono para esta arquitectura simple
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                res = loop.run_until_complete(self.weather.get_current_weather(city=city))
                loop.close()
                return res, "weather"
            except:
                return "Error obteniendo clima", "error"
        return "Weather offline", "error"
    
    def _handle_study_mode(self, params, source):
        return "📚 Modo Estudio Activado. Di 'resume pdf' o 'crea flashcards'.", "study"

    def _handle_study_resume(self, params, source):
        if self.study:
            path = params.get("file") or params.get("path")
            return self.study.summarize_pdf(path) if path else "Indica la ruta", "study"
        return "Study offline", "error"

    def _handle_study_flashcards(self, params, source):
         if self.study:
             return self.study.generate_flashcards(params.get("topic", "general")), "study"
         return "Study offline", "error"

    def _handle_time_date(self, params, source):
        tipo = params.get("type", "hora")
        now = datetime.datetime.now()
        if tipo == "hora": return f"🕐 {now.strftime('%H:%M')}", "sara"
        return f"📅 {now.strftime('%d/%m/%Y')}", "sara"

    def _handle_translate(self, params, source):
         return "Función de traducción simplificada", "sara"

    def _handle_calculate(self, params, source):
        try: return f"🔢 {eval(params.get('expression','0'))}", "sara"
        except: return "Error cálculo", "error"
    
    def _handle_zen_mode(self, params, source):
        if self.sys_control:
            self.sys_control.minimize_all_windows()
            import webbrowser
            webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk")
            return "🧘‍♂️ Modo Zen", "sara"
        return "Error sys", "error"

    def _handle_gestures(self, params, source):
        action = params.get("action", "toggle")
        # Logica lazy loading existente se mantendría aquí simplificada
        return f"Gestos {action}", "sara"

    def _handle_network_diag(self, params, source):
        if self.sys_control: return self.sys_control.get_network_status(), "sys"
        return "Error sys", "error"

    def _handle_sentinel_on(self, params, source):
        return "🛡️ Activando Modo Centinela...", "sentinel_on"

    def _handle_sentinel_off(self, params, source):
        return "🛡️ Desactivando Modo Centinela...", "sentinel_off"

    def _handle_ui_config(self, params, source):
        return "OPEN_SETTINGS_TAB", "ui_command"
    
    def _handle_ui_profile(self, params, source):
        if self.perfil:
             return self.perfil.get_config_summary(), "perfil"
        return "Perfil no disponible", "error"

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
            return "⚠️ Control de sistema no disponible (revisa logs).", "error"
        
        elif intent == "VOLUMEN_BAJAR":
            if self.sys_control:
                amount = params.get("amount", 10)
                return self.sys_control.adjust_volume(-amount), "sys"
            return "⚠️ Control de sistema no disponible.", "error"
        
        elif intent == "SILENCIO":
            if self.sys_control:
                return self.sys_control.mute_volume(), "sys"
            return "⚠️ Control de audio no disponible.", "error"
        
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
                city = params.get("city") or params.get("location")
                time_frame = params.get("time_frame", "current")
                
                try:
                    if time_frame == "week":
                        return asyncio.run(self.weather.get_forecast(city=city, days=7)), "weather"
                    elif time_frame == "tomorrow":
                        # Forecast de 3 días cubre mañana perfectamente
                        return asyncio.run(self.weather.get_forecast(city=city, days=3)), "weather"
                    else:
                        # "current" o default
                        return asyncio.run(self.weather.get_current_weather(city=city)), "weather"
                except Exception as e:
                    return f"Error clima: {e}", "error"

        elif intent == "MODO_ESTUDIO":
            return (
                "📚 **Modo Estudio Activado**\n\n"
                "Estoy lista para ayudarte. Puedes decirme:\n"
                "• 'Resume este PDF [ruta]'\n"
                "• 'Crea flashcards de [tema]'\n"
                "• 'Hazme un quiz'\n"
                "💡 ¿Por dónde empezamos?"
            ), "study"

        elif intent == "STUDY_RESUME_PDF":
            file_path = params.get("file") or params.get("path")
            if file_path:
                return self.study.summarize_pdf(file_path), "study"
            return "❌ Debes indicar la ruta del PDF.", "error"

        elif intent == "STUDY_FLASHCARDS":
            topic = params.get("topic")
            if topic:
                return self.study.generate_flashcards(topic), "study"
            return "❌ Dime sobre qué tema quieres las flashcards.", "error"

        
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
        
        elif intent == "CONTROL_GESTOS":
            # Activar/desactivar control por gestos con LAZY LOADING
            action = params.get("action", "toggle")
            
            # Cargar gesture controller solo cuando se necesita (primera vez)
            if not self._gesture_controller_loaded:
                try:
                    from gesture_controller import crear_gesture_controller
                    self.gesture_controller = crear_gesture_controller(self)
                    self._gesture_controller_loaded = True
                    logging.info("✅ GestureController cargado (lazy)")
                except Exception as e:
                    logging.error(f"⚠️ Error cargando GestureController: {e}")
                    return "No se pudo cargar el control por gestos. Verifica que MediaPipe esté instalado.", "error"
            
            if self.gesture_controller:
                if action == "activar" or action == "toggle":
                    return self.gesture_controller.start(), "sara"
                elif action == "desactivar":
                    return self.gesture_controller.stop(), "sara"
            return "Control por gestos no disponible.", "error"
        
        elif intent == "DIAGNOSTICO_RED":
            if self.sys_control:
                return self.sys_control.get_network_status(), "sys"
            return "❌ Control de sistema no disponible.", "error"
        
        elif intent == "CONVERSACION":
            # MEJORADO: Siempre dar feedback audible cuando no entiende
            texto_comando = params.get("text", comando)
            sugerencias = params.get("suggestions", [])
            
            # Si hay sugerencias del NLU, incluirlas en la respuesta
            if sugerencias:
                respuesta_base = "No estoy segura de entenderte. "
                if self.ia_online:
                    # Intentar entender con IA pero incluir sugerencias
                    respuesta_ia, _ = self.consultar_ia(f"El usuario dijo: '{texto_comando}'. Responde de forma breve y útil.")
                    return f"{respuesta_ia}\n\n💡 ¿Quisiste decir?\n{chr(10).join('• ' + s for s in sugerencias[:2])}", "sara"
                else:
                    # Sin IA, dar sugerencias directamente
                    return f"{respuesta_base}¿Quisiste decir?\n{chr(10).join('• ' + s for s in sugerencias[:3])}", "sara"
            
            # Si no hay sugerencias pero hay IA, intentar entender
            if self.ia_online:
                # Mejorar prompt para que la IA sea más útil cuando no entiende
                prompt_mejorado = f"""El usuario dijo: "{texto_comando}"

Si es un comando que no entendiste bien, intenta:
1. Interpretar la intención general
2. Si parece un comando de sistema (volumen, abrir app, buscar, etc.), sugiere el comando correcto
3. Si es una pregunta o charla, responde normalmente

Responde de forma breve y útil."""
                return self.consultar_ia(prompt_mejorado)
            else:
                # FALLBACK FINAL: Sin IA y sin sugerencias
                # Dar respuesta genérica pero útil
                comandos_comunes = [
                    "sube/baja el volumen",
                    "qué hora es",
                    "abre [aplicación]",
                    "busca [tema] en google",
                    "qué clima hace"
                ]
                respuesta_fallback = "No te entendí bien. ¿Puedes repetirlo de otra forma?\n\n"
                respuesta_fallback += "💡 Comandos comunes:\n" + "\n".join(f"• {c}" for c in comandos_comunes[:3])
                return respuesta_fallback, "sara"
        
        return None




    def procesar(self, comando):
        """
        Método Principal Refactorizado (Command Pattern)
        """
        cmd_clean = comando.lower().strip()
        
        # 1. Pipeline NLU (Layer 1 & 2)
        intent, params, source = "CONVERSACION", {}, "fallback"
        if self.intent_classifier:
            intent, params, source = self.intent_classifier.clasificar(comando)
        
        logging.info(f"🧠 SARA Brain: Intent={intent} Source={source}")

        # 2. Dispatch a Handlers (Comandos Específicos)
        if intent in self.handlers and source != "fallback":
            logging.info(f"⚡ Dispatching {intent} -> Handler")
            try:
                respuesta, origen = self.handlers[intent](params, source)
                # Guardar en memoria
                if self.memory: self.memory.add_turn(comando, str(respuesta), intent=intent)
                return respuesta, origen
            except Exception as e:
                logging.error(f"Error en handler {intent}: {e}")
                import traceback
                traceback.print_exc()
                return f"Hubo un error ejecutando {intent}", "error"

        # 3. Smart Router / AI General (Layer 3)
        # Si no es un comando registrado, usamos la IA para decidir o conversar
        if self.ia_online:
             logging.info("🧠 Fallback a AI Smart Router / Chat")
             contexto = ""
             if self.memory:
                 contexto = self.memory.get_context_prompt()
                 
             res, _ = self.consultar_ia(comando, contexto_extra=contexto)
             if self.memory: self.memory.add_turn(comando, res, intent="chat_ai")
             return res, "ai"
        
        # 4. Fallback Final (Sin IA, sin NLU)
        # Intentar lógica legado mínima (opcional, por ahora respuesta simple)
        fallback_msg = "No te entendí bien y no tengo conexión a la IA para aprender."
        if self.memory: self.memory.add_turn(comando, fallback_msg, intent="fail")
        return fallback_msg, "sara"
            

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
                    # Lista de modelos a probar
                    modelos_candidatos = [
                        'gemini-2.0-flash-exp',
                        'gemini-1.5-flash',
                        'gemini-pro'
                    ]
                    
                    modelo_seleccionado = None
                    
                    # Probar modelos disponibles
                    try:
                        for model_name in modelos_candidatos:
                            try:
                                genai_lib.GenerativeModel(model_name)
                                modelo_seleccionado = model_name
                                logging.info(f"✨ Modelo seleccionado: {modelo_seleccionado}")
                                break
                            except: continue
                    except: pass
                    
                    if not modelo_seleccionado: modelo_seleccionado = 'gemini-1.5-flash'

                    self.clients["Gemini"] = genai_lib.GenerativeModel(modelo_seleccionado)
                    self.ia_online = True
                    logging.info("✅ GenAI Conectado")
                except Exception as e:
                    logging.error(f"❌ Error Gemini: {e}")

    def consultar_ia(self, prompt, contexto_extra=""):
        """Consulta unificada a la IA"""
        if not self.ia_online:
            return "Lo siento, no tengo conexión cerebral (IA Offline).", "error"

        # Optimización: Si contexto es muy largo, recortar
        if len(contexto_extra) > 2000:
             contexto_extra = contexto_extra[-2000:]

        full_prompt = f"{contexto_extra}\n\nUsuario: {prompt}"
        
        try: 
            # GEMINI
            if self.preferred_provider == "Gemini" and "Gemini" in self.clients:
                 response = self.clients["Gemini"].generate_content(full_prompt)
                 return response.text, "ai"
        except Exception as e:
             logging.error(f"Error consultando IA: {e}")
             return "Hubo un error pensando la respuesta.", "error"

        return "No pude procesar tu solicitud.", "error"
    
    def abrir_inteligente(self, app_name, original_cmd):
        """Lógica inteligente de apertura de apps"""
        import AppOpener
        try:
             AppOpener.open(app_name, match_closest=True, throw_error=True)
             return f"Abriendo {app_name}", "cmd"
        except:
             return f"No encontré la app {app_name}", "error"

    def _es_similar(self, a, lista_b, umbral=0.8):
        from difflib import SequenceMatcher
        a = a.lower()
        for b in lista_b:
            if SequenceMatcher(None, a, b).ratio() > umbral:
                return True
        return False

# Lazy Imports seguros
def _lazy_import_genai():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        return None
