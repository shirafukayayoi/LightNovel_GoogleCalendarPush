# Pythonを初めて触る高校生が作る新作ラノベ自動取得コード解説

## はじめに

この記事を見てくれてくださりありがとうございます。  
プログラマー志望の高校生、白深やよいです。  
Node.jsをメインに勉強していたのですが、Pythonも使えると色々と便利だよな、、、と思い、Pythonの強みであるwebスプレイピングに挑戦してみました。  
開発してみて思ったのは、小さいことを積み重ねることが本当に大切だと学びました。  
そんなことはさておき、今回のコードを自分なりに解説してみました。  
参考になると幸いです。

## 解説

### 全体

全体はこちらになります。  

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import datetime
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import datetime, date, timedelta

# 指定する年と月
year = 2024
month = 7

# 出力する出版社を指定
target_media = ["電撃文庫", "講談社ラノベ文庫", "HJ文庫", "GA文庫", "ガガガ文庫", "ファンタジア文庫", "MF文庫J"]

# カレンダーidを指定
calendar_id = ''

# GoogleCalendarの認証情報のロード
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

# Google Calendar API の使用
service = build('calendar', 'v3', credentials=creds)

# ベースのurl
base_url = "https://books.rakuten.co.jp/calendar/001017/monthly/"
query_params = {
    "tid": f"{year}-{month:02}-01",  # ここで日付を固定してみましたが、必要に応じて変更してください
    "p": "{}",
    "s": "14",
    "#rclist": ""
}

# 日本語の日付を変換する関数
def convert_japanese_date(japanese_date_str, year):

    if '上旬' in japanese_date_str:
        return f"{year}-{month}-02"

    # 日本語の日付をパースする
    try:
        date_obj = datetime.strptime(japanese_date_str, '%m月 %d日')
    except ValueError:
        return ''  # パースできない場合も空文字列を返す
    
    # 年を追加して目的の形式に変換する
    formatted_date = date_obj.replace(year=year).strftime('%Y-%m-%d')
    return formatted_date


def get_events(service, calendar_id, time_min=None, time_max=None):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

for page in range(1, 5):
    query_params["p"] = str(page)
    url = base_url + "?" + urlencode(query_params)
    req = requests.get(url)

    if req.status_code == 200:
        req.encoding = req.apparent_encoding
        html_soup = BeautifulSoup(req.text, "html.parser")
        
        title_list = []
        date_list = []

        titles = html_soup.find_all(class_="item-title__text")
        if titles:
            for title in titles:
                title_list.append(title.get_text().strip())
        else:
            print("指定されたクラスの要素が見つかりません。")

        dates = html_soup.find_all(class_="item-release__date")
        if dates:
            for date in dates:
                date_list.append(date.get_text().strip())
        else:
            print("指定された要素は見つかりません。")

        media_items = html_soup.find_all(class_="item-title__media")

        for i, title in enumerate(title_list):
            if i < len(media_items):
                media = media_items[i].get_text().strip()
                formatted_date = convert_japanese_date(date_list[i], year)

                def check_duplicate(service, calendar_id, event_date, title):
                    time_min = (datetime.strptime(event_date, '%Y-%m-%d') + timedelta(days=-1)).strftime('%Y-%m-%d') + 'T00:00:00Z'
                    time_max = event_date + 'T00:00:00Z'
                    events = get_events(service, calendar_id, time_min, time_max)
                    
                    for event in events:
                        if event['summary'] == title and 'date' in event['start']:
                            return True
                    return False

                if check_duplicate(service, calendar_id, formatted_date, title):
                    print(f'{title} のイベントは既にカレンダーに存在します。')
                    continue

                if any(target in media for target in target_media):
                    event = {
                        'summary': title,
                        'start': {
                            'date': formatted_date,
                            'timeZone': 'Asia/Tokyo',
                        },
                        'end': {
                        'date': formatted_date,
                            'timeZone': 'Asia/Tokyo',
                        },
                    }

                    event = service.events().insert(calendarId=calendar_id, body=event).execute()
                    print(f'{title} のイベントが追加されました。')

            else:
                print(f"インデックス {i} が範囲外になったため終了します。")
                break

    else:
        print(f"リクエストが失敗しました。ステータスコード: {req.status_code}")
```

使い方に関しては、[https://github.com/shirafukayayoi/LightNovel_GoogleCalendarPush](https://github.com/shirafukayayoi/LightNovel_GoogleCalendarPush) こちらのレポジトリを見てください。  
さて、細かい解説をしていきます。

### CalendarAPIについて

```python
# GoogleCalendarの認証情報のロード
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

# Google Calendar API の使用
service = build('calendar', 'v3', credentials=creds)
```

ここの部分はテンプレートです。GoogleAPIを使うときはこのコードが必要になってきます。  
apiを利用するためには、`credentials.json`ファイルが必要になってきます。  
このファイルを取得するためには  
[[初心者向け] GoogleカレンダーにPythonから予定を追加・編集してみた](https://dev.classmethod.jp/articles/google-calendar-api-create-schedule/)  
このサイトがを参考になります。  
簡単に説明すると、  

1. [Googleの認証情報の発行](https://console.cloud.google.com/?hl=ja&project=discord-bot-405615)にアクセス
1. 検索に`GoogleCalendarAPI`と検索、有効にする。  
1. `有効なAPIとサービス`に行き、認証情報の作成。  
1. アクセスするデータの種類は**ユーザーデータ**
1. 後は流れにそって色々入力していき、完了を押すと、クライアントシークレットが発行される。　　
1. ダウンロードボタンを押し、ダウンロード
1. ダウンロードしたファイルの名前を`credentials.json`にする。  

これで`credentials.json`をダウンロードすることができます。

### ベースのURLを作成

```python
base_url = "https://books.rakuten.co.jp/calendar/001017/monthly/"
query_params = {
    "tid": f"{year}-{month:02}-01",  # ここで日付を固定してみましたが、必要に応じて変更してください
    "p": "{}",
    "s": "14",
    "#rclist": ""
}
```

ここの部分の解説をしていきます。  
ラノベの新作を取得するために使うサイトは、楽天ブックスです。  
仮に7月のラノベの情報を取得したいとき、全体のURLは`https://books.rakuten.co.jp/calendar/001017/monthly/?tid=2024-07-09&p=3&s=14#rclist`となります。  
`https://books.rakuten.co.jp/calendar/001017/monthly/`はどの月でも変わらないため、`base_url`にします。  
月によって変わる部分は、`query_params`を使うことによって後ほど追加していきます。  
`year`と`month`変数を`tid`にいれ、URLを作っています。

### 日本語の日付を変換する

```python
def convert_japanese_date(japanese_date_str, year):

    if '上旬' in japanese_date_str:
        return f"{year}-{month}-02"

    # 日本語の日付をパースする
    try:
        date_obj = datetime.strptime(japanese_date_str, '%m月 %d日')
    except ValueError:
        return ''  # パースできない場合も空文字列を返す
    
    # 年を追加して目的の形式に変換する
    formatted_date = date_obj.replace(year=year).strftime('%Y-%m-%d')
    return formatted_date
```

この部分の解説です。  
まず大前提として、楽天ブックスからラノベの発売日をwebスプレイピングをしたとき、返ってくるのは`?月　?日`になります。  
これを、GoogleCalendarAPIに入れるとき、日付は`2024-08-01`のような形式じゃないと予定を追加させることはできません。  
`2024`の年の部分に関しては、`year`変数を使えばいいとして、残りの部分はどうしよう……？となったとき、このコードを使います。  

### Googleカレンダーから予定の取得

```python
def get_events(service, calendar_id, time_min=None, time_max=None):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])
```

なんかこれでGoogleカレンダーの予定を取得できるらしいです。  
予定を取得するのに必要なのは、**カレンダーid**、**取得したい日付**です。  
`singleEvents`は繰り返しの予定を個別に分けるもの。  
`orderBy`は取得するイベントの順番の指定です。  

### webスプレイピングして、本の情報を取得

```python
for page in range(1, 5):
    query_params["p"] = str(page)
    url = base_url + "?" + urlencode(query_params)
    req = requests.get(url)

    if req.status_code == 200:
        req.encoding = req.apparent_encoding
        html_soup = BeautifulSoup(req.text, "html.parser")
        
        title_list = []
        date_list = []

        titles = html_soup.find_all(class_="item-title__text")
        if titles:
            for title in titles:
                title_list.append(title.get_text().strip())
        else:
            print("指定されたクラスの要素が見つかりません。")

        dates = html_soup.find_all(class_="item-release__date")
        if dates:
            for date in dates:
                date_list.append(date.get_text().strip())
        else:
            print("指定された要素は見つかりません。")

        media_items = html_soup.find_all(class_="item-title__media")
```

この部分の解説です。  
楽天ブックスは、大体4ページぐらいで作られているため、`for page in range(1, 5):`  
ここで、完全のURLを`url = base_url + "?" + urlencode(query_params)`で作ります。  
それをリクエスト。  
`if req.status_code == 200:`はwebサイトの通信が成功したときに実行できるようにするif文です。  
`title_list`と`date_list`で配列を作りwebサイトの本のタイトル、日付、出版社のclassを取得していきます。  
なかった場合は`else`で指定された要素を見つけられないことを通知しています。  

### カレンダーの重複確認

```python
        for i, title in enumerate(title_list):
            if i < len(media_items):
                media = media_items[i].get_text().strip()
                formatted_date = convert_japanese_date(date_list[i], year)

                def check_duplicate(service, calendar_id, event_date, title):
                    time_min = (datetime.strptime(event_date, '%Y-%m-%d') + timedelta(days=-1)).strftime('%Y-%m-%d') + 'T00:00:00Z'
                    time_max = event_date + 'T00:00:00Z'
                    events = get_events(service, calendar_id, time_min, time_max)
                    
                    for event in events:
                        if event['summary'] == title and 'date' in event['start']:
                            return True
                    return False

                if check_duplicate(service, calendar_id, formatted_date, title):
                    print(f'{title} のイベントは既にカレンダーに存在します。')
                    continue
```

この部分の解説です。  
webスプレイピングで取得した日付を、Googleカレンダーに登録できるような文字列に変換していきます。  
それを`check_duplicate`を作ることによって確認、if文で予定が重複していた場合、「イベントは既にカレンダーに存在します」と出力し、`continue`でfor文を止め、やり直します。  

### Googleカレンダーに取得したデータを追加

```python
                if any(target in media for target in target_media):
                    event = {
                        'summary': title,
                        'start': {
                            'date': formatted_date,
                            'timeZone': 'Asia/Tokyo',
                        },
                        'end': {
                        'date': formatted_date,
                            'timeZone': 'Asia/Tokyo',
                        },
                    }

                    event = service.events().insert(calendarId=calendar_id, body=event).execute()
                    print(f'{title} のイベントが追加されました。')

            else:
                print(f"インデックス {i} が範囲外になったため終了します。")
                break
```

この部分の解説です。  
`if any(target in media for target in target_media):`で指定した出版社の文字があった場合、予定を追加するようにし、  
`summary`にはタイトル、`start`には始まりの時間（今回は終日なので日付だけで良い）`end`には終わりの時間を入れる。  
`timeZone`はAsia/Tokyoで固定。日本時間になる。  
全ての本を予定に入れたら、「インデックス {i} が範囲外になったため終了します。」となる。

### もしwebスプレイピングができなかったら…

```python
    else:
        print(f"リクエストが失敗しました。ステータスコード: {req.status_code}")
```

このコードで何が駄目だったのか理由がわかります。  

## 最後に

初めてpythonを触っていましたが、自分の想像以上に面白く、  
自分のやりたいことを細かくして、1つ1つクリアしていくと実現がしやすくなると学ぶことができた。  
今後は、実行結果をDiscordに送れるようにしていきたいな。  
次はapi関係を触っていきたいです。  
