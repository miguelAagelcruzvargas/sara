# import os.path
# import datetime
# import pickle
# import logging
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# # Si modificas estos scopes, borra el archivo token.json.
# SCOPES = ['https://www.googleapis.com/auth/calendar']

# class CalendarManager:
#     def __init__(self):
#         self.creds = None
#         self.service = None
#         self.connect()

#     def connect(self):
#         """Autentica con Google Calendar API"""
#         try:
#             # Token.json guarda los tokens de acceso y refresh
#             if os.path.exists('token.json'):
#                 self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
#             # Si no hay credenciales válidas, loguearse
#             if not self.creds or not self.creds.valid:
#                 if self.creds and self.creds.expired and self.creds.refresh_token:
#                     self.creds.refresh(Request())
#                 else:
#                     if not os.path.exists('credentials.json'):
#                         logging.warning("⚠️ No se encontró credentials.json de Google Calendar")
#                         return
                    
#                     flow = InstalledAppFlow.from_client_secrets_file(
#                         'credentials.json', SCOPES)
#                     self.creds = flow.run_local_server(port=0)
                
#                 # Guardar credenciales para la próxima
#                 with open('token.json', 'w') as token:
#                     token.write(self.creds.to_json())

#             self.service = build('calendar', 'v3', credentials=self.creds)
#             logging.info("✅ Conectado a Google Calendar")

#         except Exception as e:
#             logging.error(f"❌ Error conectando a Calendar: {e}")
#             self.service = None

#     def get_next_events(self, max_results=5):
#         """Obtiene los próximos N eventos"""
#         if not self.service:
#             return "No estoy conectada al calendario."

#         try:
#             now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
#             events_result = self.service.events().list(calendarId='primary', timeMin=now,
#                                                     maxResults=max_results, singleEvents=True,
#                                                     orderBy='startTime').execute()
#             events = events_result.get('items', [])

#             if not events:
#                 return "No tienes eventos próximos."

#             respuesta = "📅 **Próximos eventos:**\n"
#             for event in events:
#                 start = event['start'].get('dateTime', event['start'].get('date'))
#                 # Formatear fecha para que sea legible
#                 # start suele venir como '2023-12-29T10:00:00-06:00'
#                 try:
#                     dt = datetime.datetime.fromisoformat(start)
#                     fecha_str = dt.strftime("%d/%m %H:%M")
#                 except:
#                     fecha_str = start # Fallback si es todo el día
                
#                 respuesta += f"• {fecha_str} - {event['summary']}\n"
            
#             return respuesta

#         except HttpError as error:
#             logging.error(f'An error occurred: {error}')
#             return "Hubo un error al leer tu calendario."

#     def create_event(self, summary, start_time_str, duration_minutes=60):
#         """
#         Crea un evento simple.
#         start_time_str: "YYYY-MM-DD HH:MM"
#         """
#         if not self.service: return "No estoy conectada al calendario."
        
#         try:
#             # Parsear fecha
#             start_dt = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
#             end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
            
#             event = {
#                 'summary': summary,
#                 'start': {
#                     'dateTime': start_dt.isoformat(),
#                     'timeZone': 'America/Mexico_City', # Ajustar según usuario
#                 },
#                 'end': {
#                     'dateTime': end_dt.isoformat(),
#                     'timeZone': 'America/Mexico_City',
#                 },
#             }

#             event = self.service.events().insert(calendarId='primary', body=event).execute()
#             return f"✅ Evento creado: {event.get('htmlLink')}"

#         except Exception as e:
#             logging.error(f"Error creando evento: {e}")
#             return "No pude crear el evento."
############ version 2

import os.path
import datetime
import logging
import asyncio
import pickle
from typing import Optional, List, Dict, Any

# Librerías de Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Manejo moderno de Zonas Horarias (Python 3.9+)
from zoneinfo import ZoneInfo 

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SARA-CAL - %(levelname)s - %(message)s')

SCOPES = ['https://www.googleapis.com/auth/calendar']

class SaraCalendar:
    def __init__(self):
        self.creds = None
        self.service = None
        self.timezone = ZoneInfo("America/Mexico_City") # Ajusta a tu zona
        
        # Inicialización síncrona de credenciales (se hace una sola vez al arrancar)
        self._authenticate()

    def _authenticate(self):
        """Maneja la autenticación OAuth2 y la creación del servicio."""
        try:
            if os.path.exists('token.json'):
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logging.info("🔄 Refrescando token de Google expirado...")
                    self.creds.refresh(Request())
                else:
                    logging.warning("⚠️ Iniciando flujo de login de navegador (Primera vez)...")
                    if not os.path.exists('credentials.json'):
                        logging.error("❌ Faltan credentials.json")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)

                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())

            self.service = build('calendar', 'v3', credentials=self.creds)
            logging.info("✅ Conexión establecida con Google Calendar API")

        except Exception as e:
            logging.error(f"❌ Error crítico en autenticación: {e}")
            self.service = None

    async def get_next_events(self, max_results=5) -> str:
        """
        Obtiene eventos de forma asíncrona (No bloquea a SARA).
        """
        if not self.service: return "No hay conexión con el calendario."

        def _blocking_call():
            # Hora actual en UTC formateada para la API
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=max_results, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])

        try:
            # EJECUTAR EN HILO SECUNDARIO
            events = await asyncio.to_thread(_blocking_call)

            if not events:
                return "No tienes eventos próximos en tu agenda."

            respuesta = "📅 **Tu Agenda:**\n"
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'Sin título')
                
                # Formateo amigable de la fecha
                try:
                    # Parsear fecha ISO
                    dt = datetime.datetime.fromisoformat(start)
                    # Convertir a zona horaria local del usuario
                    dt_local = dt.astimezone(self.timezone)
                    
                    # Lógica para "Hoy", "Mañana"
                    now_local = datetime.datetime.now(self.timezone)
                    
                    if dt_local.date() == now_local.date():
                        prefix = "Hoy a las"
                        fmt = "%H:%M"
                    elif dt_local.date() == (now_local + datetime.timedelta(days=1)).date():
                        prefix = "Mañana a las"
                        fmt = "%H:%M"
                    else:
                        prefix = "El"
                        fmt = "%d/%m a las %H:%M"

                    fecha_str = f"{prefix} {dt_local.strftime(fmt)}"
                    
                except ValueError:
                    # Eventos de todo el día (formato YYYY-MM-DD)
                    fecha_str = f"Todo el día ({start})"

                respuesta += f"• {fecha_str} -> {summary}\n"

            return respuesta

        except Exception as e:
            logging.error(f"Error leyendo eventos: {e}")
            return "Hubo un error técnico al leer tu calendario."

    async def create_event(self, summary: str, date_obj: datetime.datetime, duration_minutes: int = 60):
        """
        Crea un evento.
        Nota: Recibe un objeto datetime, no un string. El "Cerebro" de SARA debe procesar el texto a datetime.
        """
        if not self.service: return "Error de conexión."

        # Aseguramos que la fecha tenga zona horaria
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=self.timezone)

        end_dt = date_obj + datetime.timedelta(minutes=duration_minutes)

        event_body = {
            'summary': summary,
            'start': {
                'dateTime': date_obj.isoformat(),
                'timeZone': 'America/Mexico_City',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'America/Mexico_City',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        def _blocking_insert():
            return self.service.events().insert(calendarId='primary', body=event_body).execute()

        try:
            logging.info(f"Creando evento: {summary} para {date_obj}")
            event = await asyncio.to_thread(_blocking_insert)
            
            html_link = event.get('htmlLink')
            return f"✅ Evento agendado: **{summary}**.\n🔗 [Ver en Calendar]({html_link})"

        except Exception as e:
            logging.error(f"Error creando evento: {e}")
            return f"No pude agendar el evento por un error: {e}"

# --- EJEMPLO DE USO (ASÍNCRONO) ---
if __name__ == "__main__":
    async def main():
        # 1. Inicialización
        calendar = SaraCalendar()
        
        # 2. Consultar eventos
        print("--- CONSULTANDO ---")
        print(await calendar.get_next_events())
        
        # 3. Crear evento (Ejemplo: Mañana a las 5 PM)
        print("\n--- CREANDO EVENTO ---")
        
        # Simulamos que SARA entendió "Mañana a las 5pm" y calculó el datetime
        manana = datetime.datetime.now() + datetime.timedelta(days=1)
        manana = manana.replace(hour=17, minute=0, second=0, microsecond=0)
        
        res = await calendar.create_event("Reunión con Desarrolladores", manana)
        print(res)

    asyncio.run(main())