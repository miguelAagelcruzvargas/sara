"""
User Profile Manager - Gestión de preferencias personales de SARA con SQLite
"""
import sqlite3
import logging
from datetime import datetime
import json

class UserProfile:
    """Gestor de perfil de usuario usando SQLite"""
    
    DB_FILE = "sara_data.db"
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._init_database()
        self.profile = self.load_profile()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        try:
            self.conn = sqlite3.connect(self.DB_FILE, check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Tablas (compactado para no repetir todo)
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_info (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, preferred_name TEXT, age INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS voice_preferences (id INTEGER PRIMARY KEY AUTOINCREMENT, language TEXT DEFAULT 'es-ES', voice_type TEXT DEFAULT 'female', speed TEXT DEFAULT 'normal', updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS work_config (id INTEGER PRIMARY KEY AUTOINCREMENT, default_profile TEXT DEFAULT 'casa', work_start TEXT DEFAULT '09:00', work_end TEXT DEFAULT '18:00', updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS general_preferences (id INTEGER PRIMARY KEY AUTOINCREMENT, wake_words TEXT DEFAULT '["Sara", "Zara", "Sarah"]', continuous_mode INTEGER DEFAULT 1, theme TEXT DEFAULT 'dark', setup_completed INTEGER DEFAULT 0, setup_date TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Migración: Agregar columna 'city' si no existe
            try:
                self.cursor.execute("ALTER TABLE user_info ADD COLUMN city TEXT DEFAULT 'Mexico City'")
            except: pass

            self.conn.commit()
            
            # Insertar datos por defecto
            self._insert_defaults_if_empty()
            
            logging.info("✅ Base de datos SQLite inicializada")
            
        except Exception as e:
            logging.error(f"Error inicializando base de datos: {e}")
    
    def _insert_defaults_if_empty(self):
        """Inserta valores por defecto si las tablas están vacías"""
        try:
            # User info
            self.cursor.execute("SELECT COUNT(*) FROM user_info")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO user_info (name, preferred_name, city) VALUES ('Usuario', 'Usuario', 'Mexico City')")
            
            # Voice preferences
            self.cursor.execute("SELECT COUNT(*) FROM voice_preferences")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO voice_preferences DEFAULT VALUES")
            
            # Work config
            self.cursor.execute("SELECT COUNT(*) FROM work_config")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO work_config DEFAULT VALUES")
            
            # General preferences
            self.cursor.execute("SELECT COUNT(*) FROM general_preferences")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO general_preferences DEFAULT VALUES")
                
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error insertando defaults: {e}")

    def _default_data(self):
        """Inserta datos por defecto si las tablas están vacías"""
        # User Info
        self.cursor.execute("SELECT COUNT(*) FROM user_info")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO user_info (name, preferred_name, city) VALUES ('Usuario', 'Usuario', 'Mexico City')")
        
        # ... (resto igual)

    # ... (métodos intermedios)

    def load_profile(self):
        """Carga el perfil del usuario desde SQLite"""
        try:
            # Cargar user info (+city)
            self.cursor.execute("SELECT name, preferred_name, age, city FROM user_info WHERE id = 1")
            user_data = self.cursor.fetchone()
            
            # ... (resto de cargas)
            self.cursor.execute("SELECT language, voice_type, speed FROM voice_preferences WHERE id = 1")
            voice_data = self.cursor.fetchone()
            
            self.cursor.execute("SELECT default_profile, work_start, work_end FROM work_config WHERE id = 1")
            work_data = self.cursor.fetchone()
            
            self.cursor.execute("SELECT wake_words, continuous_mode, theme, setup_completed FROM general_preferences WHERE id = 1")
            pref_data = self.cursor.fetchone()
            
            return {
                "user": {
                    "name": user_data[0] if user_data else "",
                    "preferred_name": user_data[1] if user_data else "",
                    "age": user_data[2] if user_data else None,
                    "city": user_data[3] if user_data and len(user_data) > 3 else "Mexico City"
                },
                # ... (resto del dict)
                "voice": {
                    "language": voice_data[0] if voice_data else "es-ES",
                    "type": voice_data[1] if voice_data else "female",
                    "speed": voice_data[2] if voice_data else "normal"
                },
                "work": {
                    "default_profile": work_data[0] if work_data else "casa",
                    "work_hours": {
                        "start": work_data[1] if work_data else "09:00",
                        "end": work_data[2] if work_data else "18:00"
                    }
                },
                "preferences": {
                    "wake_words": json.loads(pref_data[0]) if pref_data else ["Sara", "Zara", "Sarah"],
                    "continuous_mode": bool(pref_data[1]) if pref_data else True,
                    "theme": pref_data[2] if pref_data else "dark"
                },
                "setup_completed": bool(pref_data[3]) if pref_data else False
            }
            
        except Exception as e:
            logging.error(f"Error cargando perfil: {e}")
            return self._default_profile()

    def update_user_info(self, name=None, preferred_name=None, age=None, city=None):
        """Actualiza información del usuario"""
        try:
            if name is not None:
                self.cursor.execute("UPDATE user_info SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (name,))
                self.profile["user"]["name"] = name
            if preferred_name is not None:
                self.cursor.execute("UPDATE user_info SET preferred_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (preferred_name,))
                self.profile["user"]["preferred_name"] = preferred_name
            if age is not None:
                self.cursor.execute("UPDATE user_info SET age = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (age,))
                self.profile["user"]["age"] = age
            if city is not None:
                self.cursor.execute("UPDATE user_info SET city = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (city,))
                self.profile["user"]["city"] = city
            
            self.conn.commit()
            return "✅ Información actualizada"
        except Exception as e:
            logging.error(f"Error actualizando usuario: {e}")
            return "❌ Error actualizando información"
    
    def update_voice_preferences(self, language=None, voice_type=None, speed=None):
        """Actualiza preferencias de voz"""
        try:
            if language:
                self.cursor.execute("UPDATE voice_preferences SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (language,))
                self.profile["voice"]["language"] = language
            if voice_type:
                self.cursor.execute("UPDATE voice_preferences SET voice_type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (voice_type,))
                self.profile["voice"]["type"] = voice_type
            if speed:
                self.cursor.execute("UPDATE voice_preferences SET speed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (speed,))
                self.profile["voice"]["speed"] = speed
            
            self.conn.commit()
            return "✅ Preferencias de voz actualizadas"
        except Exception as e:
            logging.error(f"Error actualizando voz: {e}")
            return "❌ Error actualizando preferencias"
    
    def update_work_profile(self, default_profile=None, start_time=None, end_time=None):
        """Actualiza perfil de trabajo"""
        try:
            if default_profile:
                self.cursor.execute("UPDATE work_config SET default_profile = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (default_profile,))
                self.profile["work"]["default_profile"] = default_profile
            if start_time:
                self.cursor.execute("UPDATE work_config SET work_start = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (start_time,))
                self.profile["work"]["work_hours"]["start"] = start_time
            if end_time:
                self.cursor.execute("UPDATE work_config SET work_end = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (end_time,))
                self.profile["work"]["work_hours"]["end"] = end_time
            
            self.conn.commit()
            return "✅ Perfil de trabajo actualizado"
        except Exception as e:
            logging.error(f"Error actualizando trabajo: {e}")
            return "❌ Error actualizando perfil"
    
    def get_config_summary(self):
        """Resumen de la configuración actual"""
        user = self.profile["user"]
        voice = self.profile["voice"]
        work = self.profile["work"]
        
        summary = "📋 TU PERFIL:\n\n"
        summary += f"👤 Nombre: {user['name'] or 'No configurado'}\n"
        summary += f"💬 Te llamo: {user['preferred_name'] or 'Usuario'}\n"
        summary += f"🎤 Idioma: {voice['language']}\n"
        summary += f"🗣️ Voz: {voice['type']}\n"
        summary += f"⚡ Velocidad: {voice['speed']}\n"
        summary += f"💼 Perfil trabajo: {work['default_profile']}\n"
        summary += f"⏰ Horario: {work['work_hours']['start']} - {work['work_hours']['end']}\n"
        
        return summary
    
    def mark_setup_complete(self):
        """Marca el setup como completado"""
        try:
            self.cursor.execute("UPDATE general_preferences SET setup_completed = 1, setup_date = CURRENT_TIMESTAMP WHERE id = 1")
            self.conn.commit()
            self.profile["setup_completed"] = True
        except Exception as e:
            logging.error(f"Error marcando setup: {e}")
    
    def is_setup_complete(self):
        """Verifica si el setup está completo"""
        return self.profile.get("setup_completed", False)
    
    def reset_profile(self):
        """Resetea el perfil a valores por defecto"""
        try:
            self.cursor.execute("DELETE FROM user_info")
            self.cursor.execute("DELETE FROM voice_preferences")
            self.cursor.execute("DELETE FROM work_config")
            self.cursor.execute("DELETE FROM general_preferences")
            self.conn.commit()
            
            self._insert_defaults_if_empty()
            self.profile = self.load_profile()
            
            logging.info("⚠️ Perfil reseteado")
            return "✅ Perfil reseteado a valores por defecto"
        except Exception as e:
            logging.error(f"Error reseteando perfil: {e}")
            return "❌ Error reseteando perfil"
    
    def get_welcome_message(self):
        """Mensaje de bienvenida personalizado"""
        name = self.profile["user"]["preferred_name"] or self.profile["user"]["name"] or "Usuario"
        return f"¡Hola {name}! Soy SARA, tu asistente personal. ¿En qué puedo ayudarte hoy?"

    def _default_profile(self):
        """Perfil por defecto (fallback)"""
        return {
            "user": {"name": "", "preferred_name": "", "age": None, "city": "Mexico City"},
            "voice": {"language": "es-ES", "type": "female", "speed": "normal"},
            "work": {"default_profile": "casa", "work_hours": {"start": "09:00", "end": "18:00"}},
            "preferences": {"wake_words": ["Sara", "Zara", "Sarah"], "continuous_mode": True, "theme": "dark"},
            "setup_completed": False
        }

    def __del__(self):
        """Cierra la conexión al destruir el objeto"""
        if self.conn:
            self.conn.close()


# Singleton
_profile_instance = None

def obtener_perfil():
    """Obtiene o crea la instancia del perfil"""
    global _profile_instance
    if _profile_instance is None:
        _profile_instance = UserProfile()
    return _profile_instance

