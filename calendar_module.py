import os.path
import datetime
import pickle
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Si modificas estos scopes, borra el archivo token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.connect()

    def connect(self):
        """Autentica con Google Calendar API"""
        try:
            # Token.json guarda los tokens de acceso y refresh
            if os.path.exists('token.json'):
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # Si no hay credenciales válidas, loguearse
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        logging.warning("⚠️ No se encontró credentials.json de Google Calendar")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Guardar credenciales para la próxima
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())

            self.service = build('calendar', 'v3', credentials=self.creds)
            logging.info("✅ Conectado a Google Calendar")

        except Exception as e:
            logging.error(f"❌ Error conectando a Calendar: {e}")
            self.service = None

    def get_next_events(self, max_results=5):
        """Obtiene los próximos N eventos"""
        if not self.service:
            return "No estoy conectada al calendario."

        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                    maxResults=max_results, singleEvents=True,
                                                    orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                return "No tienes eventos próximos."

            respuesta = "📅 **Próximos eventos:**\n"
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                # Formatear fecha para que sea legible
                # start suele venir como '2023-12-29T10:00:00-06:00'
                try:
                    dt = datetime.datetime.fromisoformat(start)
                    fecha_str = dt.strftime("%d/%m %H:%M")
                except:
                    fecha_str = start # Fallback si es todo el día
                
                respuesta += f"• {fecha_str} - {event['summary']}\n"
            
            return respuesta

        except HttpError as error:
            logging.error(f'An error occurred: {error}')
            return "Hubo un error al leer tu calendario."

    def create_event(self, summary, start_time_str, duration_minutes=60):
        """
        Crea un evento simple.
        start_time_str: "YYYY-MM-DD HH:MM"
        """
        if not self.service: return "No estoy conectada al calendario."
        
        try:
            # Parsear fecha
            start_dt = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'America/Mexico_City', # Ajustar según usuario
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'America/Mexico_City',
                },
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return f"✅ Evento creado: {event.get('htmlLink')}"

        except Exception as e:
            logging.error(f"Error creando evento: {e}")
            return "No pude crear el evento."
