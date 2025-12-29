import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

CONFIG_FILE = "sara_config.json"

# Determinar la ruta del archivo .env
# Para desarrollo: usar .env en el directorio actual
# Para ejecutable: usar %APPDATA%\SARA\.env
def obtener_ruta_env():
    """Determina la ruta del archivo .env según el contexto de ejecución."""
    if getattr(sys, 'frozen', False):
        # Ejecutable (PyInstaller)
        appdata = os.getenv('APPDATA')
        sara_dir = Path(appdata) / 'SARA'
        sara_dir.mkdir(exist_ok=True)
        return sara_dir / '.env'
    else:
        # Desarrollo
        return Path('.env')

# Cargar variables de entorno desde .env
env_path = obtener_ruta_env()
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logging.info(f"✓ Variables de entorno cargadas desde: {env_path}")
else:
    logging.warning(f"⚠ Archivo .env no encontrado en: {env_path}")

class ConfigManager:
    @staticmethod
    def cargar_config():
        """
        Carga la configuración con el siguiente orden de prioridad:
        1. Variables de entorno (.env o sistema)
        2. Archivo sara_config.json (solo configuración no sensible)
        3. Valores por defecto
        """
        default = {
            "provider": "Gemini", 
            "gemini_key": "",
            "groq_key": "",
            "openai_key": "",
            "theme": "Dark",
            "git_path": "C:/Program Files/Git/bin/git.exe"
        }
        
        # PRIORIDAD 1: Variables de entorno (MÁS SEGURO)
        config = {
            "provider": os.getenv("SARA_PROVIDER", default["provider"]),
            "gemini_key": os.getenv("GEMINI_API_KEY", ""),
            "groq_key": os.getenv("GROQ_API_KEY", ""),
            "openai_key": os.getenv("OPENAI_API_KEY", ""),
            "weather_key": os.getenv("WEATHER_API_KEY", ""), # NUEVO
            "theme": os.getenv("SARA_THEME", default["theme"]),
            "git_path": os.getenv("SARA_GIT_PATH", default["git_path"])
        }
        
        # PRIORIDAD 2: Archivo JSON (solo configuración no sensible)
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    
                    # Solo usar del archivo si no está en variables de entorno
                    if not config["provider"] or config["provider"] == default["provider"]:
                        config["provider"] = file_config.get("provider", default["provider"])
                    
                    if not config["theme"] or config["theme"] == default["theme"]:
                        config["theme"] = file_config.get("theme", default["theme"])
                    
                    if not config["git_path"] or config["git_path"] == default["git_path"]:
                        config["git_path"] = file_config.get("git_path", default["git_path"])
                        
            except Exception as e:
                logging.warning(f"Error leyendo config: {e}")
        
        return {**default, **config}

    @staticmethod
    def guardar_config(data):
        """
        Guarda la configuración de forma segura.
        Las API keys NUNCA se guardan en el archivo JSON.
        """
        # Solo guardar configuración no sensible
        safe_data = {
            "provider": data.get("provider", "Gemini"),
            "theme": data.get("theme", "Dark"),
            "git_path": data.get("git_path", "C:/Program Files/Git/bin/git.exe")
        }
        
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(safe_data, f, indent=2)
            logging.info("✓ Configuración guardada en sara_config.json")
        except Exception as e:
            logging.error(f"Error guardando config: {e}")
    
    @staticmethod
    def guardar_api_keys(gemini_key="", groq_key="", openai_key="", weather_key="", provider="Gemini"):
        """
        Guarda las API keys en el archivo .env de forma segura.
        """
        env_path = obtener_ruta_env()
        
        try:
            # Leer contenido actual del .env si existe
            env_content = {}
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()
            
            # Actualizar con nuevos valores
            if gemini_key:
                env_content['GEMINI_API_KEY'] = gemini_key
            if groq_key:
                env_content['GROQ_API_KEY'] = groq_key
            if openai_key:
                env_content['OPENAI_API_KEY'] = openai_key
            if weather_key:
                env_content['WEATHER_API_KEY'] = weather_key
            if provider:
                env_content['SARA_PROVIDER'] = provider
            
            # Escribir archivo .env
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write("# SARA - Configuración de API Keys\n")
                f.write("# MANTÉN ESTE ARCHIVO SEGURO Y PRIVADO\n\n")
                
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
            
            logging.info(f"✓ API keys guardadas en: {env_path}")
            
            # Recargar variables de entorno
            load_dotenv(dotenv_path=env_path, override=True)
            
            return True
        except Exception as e:
            logging.error(f"Error guardando API keys: {e}")
            return False
    
    @staticmethod
    def validar_configuracion():
        """
        Valida que existan las API keys necesarias.
        Retorna (es_valido, mensaje)
        """
        config = ConfigManager.cargar_config()
        provider = config.get("provider", "Gemini")
        
        # Verificar que exista al menos una API key del proveedor seleccionado
        if provider == "Gemini" and not config.get("gemini_key"):
            return False, "Falta la API key de Gemini"
        elif provider == "Groq" and not config.get("groq_key"):
            return False, "Falta la API key de Groq"
        elif provider == "OpenAI" and not config.get("openai_key"):
            return False, "Falta la API key de OpenAI"
        
        return True, "Configuración válida"
    
    @staticmethod
    def necesita_configuracion_inicial():
        """
        Verifica si es necesario mostrar la GUI de configuración inicial.
        """
        config = ConfigManager.cargar_config()
        
        # Si no hay ninguna API key configurada, necesita setup
        tiene_alguna_key = (
            config.get("gemini_key") or 
            config.get("groq_key") or 
            config.get("openai_key")
        )
        
        return not tiene_alguna_key
    
    @staticmethod
    def obtener_instrucciones_setup():
        """
        Retorna instrucciones para configurar SARA.
        """
        env_path = obtener_ruta_env()
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║          CONFIGURACIÓN INICIAL DE S.A.R.A.                   ║
╚══════════════════════════════════════════════════════════════╝

Para usar SARA necesitas al menos una API key de IA:

1. GEMINI (Recomendado - Gratis):
   → https://aistudio.google.com/app/apikey
   
2. GROQ (Alternativa - Gratis):
   → https://console.groq.com/keys
   
3. OPENAI (Opcional - De pago):
   → https://platform.openai.com/api-keys

═══════════════════════════════════════════════════════════════

OPCIÓN A - Configuración Automática:
   Ejecuta: python first_run_setup.py

OPCIÓN B - Configuración Manual:
   1. Copia el archivo .env.example a .env
   2. Edita .env y pega tus API keys
   3. Guarda el archivo
   
   Ubicación del .env: {env_path}

═══════════════════════════════════════════════════════════════
"""

# Importar sys para la función obtener_ruta_env
import sys
