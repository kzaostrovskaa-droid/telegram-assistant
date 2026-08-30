import os
import json
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    
    # Пробуем загрузить токен из переменной окружения
    token_b64 = os.getenv('GOOGLE_TOKEN_PICKLE')
    if token_b64:
        import io
        token_bytes = base64.b64decode(token_b64)
        creds = pickle.loads(token_bytes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Обновляем токен в переменной (для Railway)
            import base64
            token_b64 = base64.b64encode(pickle.dumps(creds)).decode()
            print(f"GOOGLE_TOKEN_PICKLE={token_b64}")
        else:
            # Локальная авторизация через файл
            if os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                raise Exception("No Google credentials found")
    
    return build('calendar', 'v3', credentials=creds)

def add_event(summary, description, start_time, end_time):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': end_time, 'timeZone': 'Europe/Moscow'},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')