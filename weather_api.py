import aiohttp
import asyncio
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
import urllib.parse

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WEATHER - %(levelname)s - %(message)s')

class SaraWeather:
    """
    Módulo climático Asíncrono para SARA.
    Integración robusta: Caché -> OpenWeatherMap -> Open-Meteo -> wttr.in
    """
    
    def __init__(self, api_key: Optional[str] = None, default_city: str = "Mexico City"):
        self.default_city = default_city
        
        # Intentamos cargar config si existe, sino usamos el argumento
        try:
            from config import ConfigManager
            config = ConfigManager.cargar_config()
            self.api_key = api_key or config.get("weather_key")
        except ImportError:
            self.api_key = api_key or "TU_API_KEY_AQUI" # Pon tu Key real o déjalo None

        self.base_url_owm = "http://api.openweathermap.org/data/2.5"
        
        # SISTEMA DE CACHÉ
        # Estructura: { "ciudad": { "tipo": { "timestamp": 123, "data": "..." } } }
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.CACHE_TTL = 900  # 15 minutos de memoria (900 seg)

    async def _get_session(self):
        """Genera una sesión optimizada para no abrir/cerrar conexiones a cada rato"""
        return aiohttp.ClientSession(headers={
            'User-Agent': 'SARA-Assistant/2.0 (Compatible;Bot)',
            'Accept-Language': 'es-ES,es;q=0.9'
        })

    async def get_current_weather(self, city: Optional[str] = None) -> str:
        """Obtiene el clima actual orquestando todas las fuentes."""
        city = city or self.default_city
        
        # 1. VERIFICAR CACHÉ (Velocidad extrema)
        if self._is_cache_valid(city, "current"):
            logging.info(f"⚡ Usando memoria caché para {city}")
            return self._cache[city]["current"]["data"]

        async with await self._get_session() as session:
            result = None
            
            # 2. INTENTO A: Open-Meteo (PRIORIDAD: El mejor gratuito y científico)
            result = await self._fetch_open_meteo(session, city)
            
            # 3. INTENTO B: OpenWeatherMap (Respaldo si hay Key)
            if not result and self.api_key and "TU_API_KEY" not in self.api_key:
                result = await self._fetch_openweathermap(session, city)

            # 4. INTENTO C: wttr.in (Respaldo final)
            if not result:
                result = await self._fetch_wttr(session, city)

            # Guardar en caché si hubo éxito
            if result:
                self._update_cache(city, "current", result)
                return result
            
            return "Lo siento, no pude conectar con ningún servicio de clima. Verifica tu conexión."

    async def get_forecast(self, city: Optional[str] = None, days: int = 3) -> str:
        """Pronóstico de N días."""
        city = city or self.default_city
        cache_key = f"forecast_{days}"
        
        if self._is_cache_valid(city, cache_key):
            return self._cache[city][cache_key]["data"]

        async with await self._get_session() as session:
            # Priorizamos Open-Meteo para pronósticos porque es GRATIS y detalla lluvia %
            result = await self._fetch_open_meteo_forecast(session, city, days)
            
            if not result and self.api_key:
                result = await self._fetch_owm_forecast(session, city)

            if result:
                self._update_cache(city, cache_key, result)
                return result
            
            return "No pude obtener el pronóstico detallado hoy."

    async def _fetch_open_meteo_forecast(self, session, city, days=3):
        """Pronóstico detallado gratuito"""
        try:
            lat, lon, real_name = await self._geocodificar(session, city)
            if not lat: return None

            # Limitar a máximo 7 días (Open-Meteo free soporta más, pero 7 es buen límite)
            if days > 7: days = 7
            
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max&forecast_days={days}&timezone=auto"
            async with session.get(url) as resp:
                data = await resp.json()
                daily = data["daily"]
                
                msg = f"📅 Pronóstico para {real_name} ({days} días):\n"
                dias_semana = ["Hoy", "Mañana", "Pasado mañana"]
                
                # Para días más allá de 3, usar nombre del día (Lunes, Martes...)
                import datetime
                dt_hoy = datetime.datetime.now()
                
                for i in range(days):
                    # Título del día
                    if i < 3:
                        dia_txt = dias_semana[i]
                    else:
                        # Calcular nombre del día
                        dt_target = dt_hoy + datetime.timedelta(days=i)
                        nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                        dia_txt = nombres_dias[dt_target.weekday()]
                    
                    min_t = round(daily['temperature_2m_min'][i])
                    max_t = round(daily['temperature_2m_max'][i])
                    desc = self._wmo_code_to_text(daily['weather_code'][i])
                    rain = daily['precipitation_probability_max'][i]
                    
                    # Highlight si llueve
                    rain_icon = "☔" if rain > 40 else "💧"
                    msg += f"• {dia_txt}: {min_t}°/{max_t}°. {desc}. {rain_icon} Lluvia {rain}%\n"
                return msg
        except Exception as e:
            logging.error(f"Fallo Forecast Open-Meteo: {e}")
        return None

    # --- UTILIDADES INTERNAS ---

    async def _geocodificar(self, session, city):
        """Convierte nombre de ciudad a lat/lon"""
        try:
            city_encoded = urllib.parse.quote(city)
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_encoded}&count=1&language=es&format=json"
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get("results"):
                    res = data["results"][0]
                    return res["latitude"], res["longitude"], res["name"]
                
                # FALLBACK: Si falla "Loma Bonita, Oaxaca", probar solo "Loma Bonita"
                if "," in city:
                    simple_city = city.split(",")[0].strip()
                    logging.info(f"🔄 Reintentando geocodificación con: {simple_city}")
                    encoded_simple = urllib.parse.quote(simple_city)
                    url_simple = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_simple}&count=1&language=es&format=json"
                    async with session.get(url_simple) as resp2:
                         data2 = await resp2.json()
                         if data2.get("results"):
                             res = data2["results"][0]
                             return res["latitude"], res["longitude"], res["name"]
                
                logging.warning(f"⚠️ Geocodificación sin resultados para: {city}")

        except Exception as e:
            logging.error(f"❌ Error en Geocodificación: {e}")
            logging.error(f"URL fallida: {url}")
        return None, None, None

    def _generar_variantes(self, city):
        """Genera variantes de nombres para reintentos"""
        variantes = []
        if "MX" not in city.upper(): variantes.append(f"{city}, MX")
        parts = city.split()
        if len(parts) > 1:
            con_coma = " ".join(parts[:-1]) + ", " + parts[-1]
            variantes.append(con_coma)
            if "MX" not in con_coma.upper(): variantes.append(f"{con_coma}, MX")
        return variantes

    def _is_cache_valid(self, city, type_key):
        if city in self._cache and type_key in self._cache[city]:
            age = time.time() - self._cache[city][type_key]["timestamp"]
            return age < self.CACHE_TTL
        return False

    def _update_cache(self, city, type_key, data):
        if city not in self._cache: self._cache[city] = {}
        self._cache[city][type_key] = {"timestamp": time.time(), "data": data}

    def _translate_wttr(self, text):
        mapping = {
            "Sunny": "Soleado", "Clear": "Despejado", "Partly cloudy": "Parcialmente nublado",
            "Cloudy": "Nublado", "Overcast": "Cubierto", "Mist": "Neblina", "Rain": "Lluvia",
            "Light rain": "Lluvia ligera", "Heavy rain": "Lluvia fuerte"
        }
        return mapping.get(text, text)

    def _wmo_code_to_text(self, code):
        codes = {
            0: "Cielo despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
            45: "Niebla", 48: "Niebla escarchada", 51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna densa",
            61: "Lluvia leve", 63: "Lluvia moderada", 65: "Lluvia fuerte", 80: "Chubascos leves",
            95: "Tormenta eléctrica", 96: "Tormenta con granizo"
        }
        return codes.get(code, "Condiciones variables")

    async def _fetch_open_meteo(self, session, city):
        """Obtiene clima actual de Open-Meteo (GRATIS)"""
        try:
            lat, lon, real_name = await self._geocodificar(session, city)
            if not lat:
                return None
            
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
            async with session.get(url) as resp:
                data = await resp.json()
                current = data["current"]
                
                temp = round(current["temperature_2m"])
                humidity = current["relative_humidity_2m"]
                wind = round(current["wind_speed_10m"])
                desc = self._wmo_code_to_text(current["weather_code"])
                
                return f"🌡️ {real_name}: {temp}°C, {desc}. 💧 Humedad {humidity}%, 💨 Viento {wind} km/h"
        except Exception as e:
            logging.error(f"Error Open-Meteo current: {e}")
        return None

    async def _fetch_openweathermap(self, session, city):
        """Obtiene clima de OpenWeatherMap (requiere API key)"""
        try:
            url = f"{self.base_url_owm}/weather?q={city}&appid={self.api_key}&units=metric&lang=es"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                
                temp = round(data["main"]["temp"])
                desc = data["weather"][0]["description"].capitalize()
                humidity = data["main"]["humidity"]
                wind = round(data["wind"]["speed"] * 3.6)  # m/s a km/h
                
                return f"🌡️ {city}: {temp}°C, {desc}. 💧 Humedad {humidity}%, 💨 Viento {wind} km/h"
        except Exception as e:
            logging.error(f"Error OpenWeatherMap: {e}")
        return None

    async def _fetch_wttr(self, session, city):
        """Fallback final usando wttr.in (SIEMPRE funciona)"""
        try:
            city_encoded = urllib.parse.quote(city)
            url = f"https://wttr.in/{city_encoded}?format=%C+%t+%h+%w&lang=es"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                text = await resp.text()
                # Formato: "Despejado +15°C 60% 10km/h"
                parts = text.strip().split()
                if len(parts) >= 3:
                    desc = self._translate_wttr(parts[0])
                    temp = parts[1]
                    humidity = parts[2] if len(parts) > 2 else "N/A"
                    wind = parts[3] if len(parts) > 3 else "N/A"
                    return f"🌡️ {city}: {temp}, {desc}. 💧 Humedad {humidity}, 💨 Viento {wind}"
                return text.strip()
        except Exception as e:
            logging.error(f"Error wttr.in: {e}")
        return None

    async def _fetch_owm_forecast(self, session, city):
        # Placeholder para mantener compatibilidad si decides reactivar el forecast de OWM
        return None 

# Singleton
_weather_instance = None

def obtener_weather(api_key: Optional[str] = None, city: str = "Mexico City") -> SaraWeather:
    global _weather_instance
    if _weather_instance is None:
        _weather_instance = SaraWeather(api_key=api_key, default_city=city)
    else:
        # Si ya existe, actualizamos la ciudad por defecto si se provee una diferente
        if city != "Mexico City":
            _weather_instance.default_city = city
            
    return _weather_instance

# --- EJEMPLO DE USO (Así debes llamarlo ahora) ---
if __name__ == "__main__":
    import asyncio
    import sys
    
    # Fix Loop en Windows para pruebas locales
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    async def main():
        # Instancia
        sara_clima = SaraWeather(api_key=None, default_city="Loma Bonita, Oaxaca")
        
        print("--- 1. CONSULTA REAL (Internet) ---")
        print(await sara_clima.get_current_weather())
        
        print("\n--- 2. CONSULTA RÁPIDA (Caché) ---")
        # Esto será instantáneo
        print(await sara_clima.get_current_weather())
        
        print("\n--- 3. PRONÓSTICO ---")
        print(await sara_clima.get_forecast())

    asyncio.run(main())