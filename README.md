# LightNovel_GoogleCalendarPush

## 説明

このpythonコードは、楽天ブックスの`https://books.rakuten.co.jp/calendar/001017/monthly/`のサイトから自動的にライトノベルのタイトル、発売日を取得し、Googleカレンダーに予定を追加するためのコードです。  
7月上旬と書いてあるラノベは、その月の1日に追加されます。

## 使い方

1. このコードで使われるパッケージをインストールします。  
   `pip install -r requirements.txt`をcmdで実行してください。
1. `LightNovel_GoogleCalendarPush.py`のコードを自分の用途に合わせて変えていきます。
   1. `year`と`month`の変数を、ラノベの情報を取得したい年と月に合わせて変えてください。
   1. 次に、`calendar_id`の変数に、自分がGoogleカレンダーの予定に入れたいカレンダーIDを入れます。
   1. [GoogleカレンダーIDの調べ方](https://qiita.com/mikeneko_t98/items/60e264941492d0b44fe5)←わからない人はこれを見てください。
   1. `target_media`に自動取得し、Googleカレンダーに入れたい出版社を""と,で入れます。
1. GoogleAPIの取得
   1. apiの取得は、[[初心者向け] GoogleカレンダーにPythonから予定を追加・編集してみた](https://dev.classmethod.jp/articles/google-calendar-api-create-schedule/)  
   このサイトを参考にしてください。ダウンロードしたjsonファイルは`credentials.json`と名前を変更してこのプログラムと同じディレクトリに入れてください。
1. 実行！  
   このコードを実行してください。  
   上手く行けば、こんな感じになるはずです。
   ![実行結果](image.png)

## 既存の問題

- Googleカレンダーの設定の方で、自動的に通知の時間を設定している場合、重複機能が使えません。

## 宣伝

[Pythonを初めて触る高校生が作った新作ラノベ自動取得コード解説](https://zenn.dev/shirafukayayoi/articles/3d89539bf26c3d)  
Zennにこのコードの解説をあげたので見て！！！！！！！！！！！！！
