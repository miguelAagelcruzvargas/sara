"""
SARA - Weather Integration
Integración robusta SIN API KEY (wttr.in + Open-Meteo)
"""
import requests
import logging
from typing import Dict, Optional

class WeatherAPI:
    """
    Obtiene clima real usando fuentes gratuitas sin API Key.
    Estrategia:
    1. wttr.in (JSON/Texto) - Muy preciso
    2. Open-Meteo (Backup) - Datos científicos
    """
    
    
    def __init__(self, api_key: Optional[str] = None, city: str = "Mexico City"):
        from config import ConfigManager # Importación local para evitar ciclos
        config = ConfigManager.cargar_config()
        
        self.city = city
        # Prioridad: Argumento -> Config -> Hardcoded (Backup)
        self.api_key = api_key or config.get("weather_key") or "98bad09df97825cc5cba7ff3c56a9e42"
        
        self.session = requests.Session()
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_current_weather(self, city: Optional[str] = None) -> str:
        """Obtiene clima actual (Prioridad: OpenWeatherMap -> wttr.in -> Open-Meteo)"""
        city = city or self.city
        
        # Intento 1: OpenWeatherMap (API KEY)
        if self.api_key:
            try:
                return self._get_openweathermap(city)
            except Exception as e:
                logging.debug(f"Fallo OWM: {e}")

        # Intento 2: wttr.in (Formato j1)
        try:
            return self._get_wttr_json(city)
        except Exception as e:
            logging.debug(f"Fallo wttr JSON: {e}")
            
        # Intento 3: wttr.in (Texto simple)
        try:
            return self._get_wttr_text(city)
        except Exception as e:
            logging.debug(f"Fallo wttr texto: {e}")
            
        # Intento 4: Open-Meteo (Backup final)
        try:
            return self._get_open_meteo(city)
        except Exception as e:
            logging.error(f"Fallo Open-Meteo: {e}")
            
        return "Lo siento, no pude conectar con ningún servicio de clima. Verifica tu internet."

    def _get_openweathermap(self, city):
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "es"
        }
        resp = self.session.get(url, params=params, timeout=5)
        
        # --- REINTENTO INTELIGENTE SI NO ENCUENTRA CIUDAD ---
        if resp.status_code == 404:
            logging.info(f"Ciudad '{city}' no encontrada. Probando variantes...")
            variantes = []
            if "MX" not in city.upper() and "MEXICO" not in city.upper():
                variantes.append(f"{city}, MX")
            
            # Si es "Loma Bonita Oaxaca" -> "Loma Bonita, Oaxaca"
            parts = city.split()
            if len(parts) > 1:
                # Asumir último token es estado
                con_coma = " ".join(parts[:-1]) + ", " + parts[-1]
                variantes.append(con_coma)
                if "MX" not in con_coma.upper():
                    variantes.append(f"{con_coma}, MX")
            
            for var in variantes:
                logging.info(f"Probando variante: {var}")
                params["q"] = var
                resp = self.session.get(url, params=params, timeout=5)
                if resp.status_code == 200:
                    logging.info(f"✅ Encontrado con: {var}")
                    break
        # ----------------------------------------------------

        resp.raise_for_status()
        data = resp.json()
        
        temp = round(data["main"]["temp"])
        hum = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        wind = round(data["wind"]["speed"] * 3.6)
        
        return f"🌡️ {temp}°C en {city}. {desc}. Humedad {hum}%. Viento {wind} km/h."
            
    def _get_wttr_json(self, city):
        url = f"https://wttr.in/{city}?format=j1"
        resp = self.session.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        current = data['current_condition'][0]
        
        temp = current['temp_C']
        desc = self._translate(current['weatherDesc'][0]['value'])
        hum = current['humidity']
        
        return f"🌡️ {temp}°C en {city}. {desc}. Humedad {hum}%."

    def _get_wttr_text(self, city):
        # Formato: Condición:Temperatura
        url = f"https://wttr.in/{city}?format=%C:%t&lang=es"
        resp = self.session.get(url, timeout=5)
        text = resp.text.strip() # Ej: "Despejado:+25°C"
        
        if ":" in text:
            cond, temp = text.split(":", 1)
            return f"🌡️ {temp} en {city}. {cond}."
        return f"Clima en {city}: {text}"

    def _get_open_meteo(self, city):
        # 1. Geocodificar
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=es&format=json"
        geo_resp = self.session.get(geo_url, timeout=5)
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            return f"No encontré la ciudad {city}."
            
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        
        # 2. Clima
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto"
        w_resp = self.session.get(weather_url, timeout=5)
        w_data = w_resp.json()
        
        temp = w_data["current"]["temperature_2m"]
        hum = w_data["current"]["relative_humidity_2m"]
        code = w_data["current"]["weather_code"]
        desc = self._get_wmo_code(code)
        
        return f"🌡️ {temp}°C en {city}. {desc}. Humedad {hum}%."

    def get_forecast(self, city: Optional[str] = None) -> str:
        # Intento 1: OpenWeatherMap (API KEY)
        city = city or self.city
        if self.api_key:
            try:
                return self._get_openweathermap_forecast(city)
            except Exception as e:
                logging.debug(f"Fallo OWM Forecast: {e}")

        # Intento 2: Open-Meteo
        try:
            return self._get_open_meteo_forecast(city)
        except:
            return "No pude obtener el pronóstico detallado hoy."

    def _get_openweathermap_forecast(self, city):
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "es",
            "cnt": 24 # 3 días (8 x 3)
        }
        resp = self.session.get(url, params=params, timeout=5)

        # --- REINTENTO INTELIGENTE FORECAST ---
        if resp.status_code == 404:
            logging.info(f"Forecast '{city}' no encontrada. Probando variantes...")
            variantes = []
            if "MX" not in city.upper() and "MEXICO" not in city.upper():
                variantes.append(f"{city}, MX")
            
            parts = city.split()
            if len(parts) > 1:
                con_coma = " ".join(parts[:-1]) + ", " + parts[-1]
                variantes.append(con_coma)
                if "MX" not in con_coma.upper():
                    variantes.append(f"{con_coma}, MX")
            
            for var in variantes:
                logging.info(f"Probando variante forecast: {var}")
                params["q"] = var
                resp = self.session.get(url, params=params, timeout=5)
                if resp.status_code == 200:
                    break
        # ----------------------------------------------------

        resp.raise_for_status()
        data = resp.json()
        
        forecast_text = f"📅 Pronóstico OWM para {city}:\n"
        from datetime import datetime
        daily_data = {}
        
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%A")
            if date not in daily_data:
                daily_data[date] = { "max": -100, "min": 100, "desc": item["weather"][0]["description"] }
            
            daily_data[date]["max"] = max(daily_data[date]["max"], item["main"]["temp_max"])
            daily_data[date]["min"] = min(daily_data[date]["min"], item["main"]["temp_min"])
            
        for day, info in list(daily_data.items())[:3]:
            forecast_text += f"\n{day}: {round(info['min'])}°-{round(info['max'])}°C, {info['desc'].capitalize()}"
            
        return forecast_text

    def _get_open_meteo_forecast(self, city):
        try:
            # 1. Geocodificar
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=es&format=json"
            geo_resp = self.session.get(geo_url, timeout=5)
            geo_data = geo_resp.json()
            
            if not geo_data.get("results"):
                return f"No encontré la ciudad {city}."
                
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            
            # 2. Pronóstico diario (3 días)
            from datetime import datetime
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code&timezone=auto&forecast_days=3"
            w_resp = self.session.get(weather_url, timeout=5)
            w_data = w_resp.json()
            
            daily = w_data["daily"]
            times = daily["time"]
            maxs = daily["temperature_2m_max"]
            mins = daily["temperature_2m_min"]
            probs = daily["precipitation_probability_max"]
            codes = daily["weather_code"]
            
            text = f"📅 Pronóstico para {city}:\n"
            
            dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            
            for i in range(len(times)):
                dt = datetime.strptime(times[i], "%Y-%m-%d")
                dia_nombre = dias_semana[dt.weekday()]
                if i == 0: dia_nombre = "Hoy"
                elif i == 1: dia_nombre = "Mañana"
                
                desc = self._get_wmo_code(codes[i])
                text += f"{dia_nombre}: {mins[i]}°-{maxs[i]}°C. {desc}. Lluvia {probs[i]}%.\n"
                
            return text
            
        except Exception as e:
            logging.error(f"Error Open-Meteo Forecast: {e}")
            return "No pude obtener el pronóstico detallado."

    def _translate(self, text):
        mapping = {
            "Sunny": "Soleado", "Clear": "Despejado", "Partly cloudy": "Parcialmente nublado",
            "Cloudy": "Nublado", "Overcast": "Cubierto", "Mist": "Neblina", "Rain": "Lluvia"
        }
        return mapping.get(text, text)
        
    def _get_wmo_code(self, code):
        # WMO Weather interpretation codes (WW)
        if code == 0: return "Cielo despejado"
        if code in [1, 2, 3]: return "Parcialmente nublado"
        if code in [45, 48]: return "Niebla"
        if code in [51, 53, 55]: return "Llovizna"
        if code in [61, 63, 65]: return "Lluvia"
        if code in [71, 73, 75]: return "Nieve"
        if code in [95, 96, 99]: return "Tormenta eléctrica"
        return "Condiciones variables"

# Singleton
_weather_instance = None
def obtener_weather(api_key: Optional[str] = None, city: str = "Mexico City"):
    global _weather_instance
    if _weather_instance is None:
        _weather_instance = WeatherAPI(api_key, city)
    return _weather_instance
