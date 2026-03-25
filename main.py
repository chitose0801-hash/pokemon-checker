import requests
import os

LINE_TOKEN = os.environ.get('LINE_TOKEN')

def test_send():
    if not LINE_TOKEN:
        print("エラー: LINE_TOKENが設定されていません")
        return

    url = "https://notify-bot.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": "テスト送信です！これが届けば設定はOKです。"}
    
    res = requests.post(url, headers=headers, data=data)
    print(f"ステータスコード: {res.status_code}")
    print(f"レスポンス: {res.text}")

if __name__ == "__main__":
    test_send()
