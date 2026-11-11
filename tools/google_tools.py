import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_google_schedule(task_name: str, start_date: str, end_date: str = None) -> str:
    try:
        service = get_calendar_service()
        event = {
            'summary': task_name,
            'start': {'date': start_date, 'timeZone': 'Asia/Seoul'},
            'end': {'date': end_date or start_date, 'timeZone': 'Asia/Seoul'},
        }
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        return f"구글 캘린더 등록 성공: '{task_name}' 일정이 추가되었습니다. (링크: {event_result.get('htmlLink')})"
    except Exception as e:
        return f"구글 캘린더 등록 실패: {e}"

def delete_google_schedule(task_name: str) -> str:
    try:
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId='primary', q=task_name, singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"구글 캘린더에서 '{task_name}' 일정을 찾을 수 없습니다."
        
        deleted_count = 0
        for event in events:
            if task_name.lower() in event.get('summary', '').lower():
                service.events().delete(calendarId='primary', eventId=event['id']).execute()
                deleted_count += 1
                
        if deleted_count == 0:
            return f"구글 캘린더에서 일치하는 이름의 일정을 찾지 못했습니다."
            
        return f"구글 캘린더에서 '{task_name}' 일정 {deleted_count}개가 성공적으로 삭제되었습니다."
    except Exception as e:
        return f"구글 캘린더 삭제 API 통신 오류: {e}"