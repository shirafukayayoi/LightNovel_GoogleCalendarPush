from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

# 1. 認証情報のロード
creds = None
# credentials.json ファイルに保存された認証情報をロードする
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

# 認証情報がない場合や期限切れの場合は、ユーザーに認証を求める
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', ['https://www.googleapis.com/auth/calendar.events'])
        creds = flow.run_local_server(port=0)
    # 認証情報を保存する
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# 2. Google Calendar API の使用
service = build('calendar', 'v3', credentials=creds)

# 終日イベントの作成
event = {
    'summary': 'Google Calendar APIでの終日テストイベント',
    'location': '東京',
    'description': 'PythonでGoogle Calendar APIを使って終日イベントを作成します。',
    'start': {
        'date': '2024-07-10',
        'timeZone': 'Asia/Tokyo',
    },
    'end': {
        'date': '2024-07-14',
        'timeZone': 'Asia/Tokyo',
    },
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'popup', 'minutes': 30},
        ],
    },
}

# 特定のカレンダーIDを指定してイベントを追加する
calendar_id = '3913e0f7c529226dbd6b896cfc7e2c4cd82cde7fab054f31a05c2f78250ee5ea@group.calendar.google.com'
event = service.events().insert(calendarId=calendar_id, body=event).execute()
print('終日イベントが追加されました。')
