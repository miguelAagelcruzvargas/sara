from weather_api import obtener_weather

print("Probando API del Clima...")
try:
    weather = obtener_weather()
    clima = weather.get_current_weather()
    print(f"Resultado Clima: {clima}")
    
    pronostico = weather.get_forecast()
    print(f"Resultado Pronóstico (primeros 50 caracteres): {pronostico[:50]}...")
except ImportError:
    print("ERROR: Falta instalar 'requests'. Ejecuta: pip install requests")
except Exception as e:
    print(f"ERROR: {e}")
