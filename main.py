import requests
from bs4 import BeautifulSoup
import os

# 抽選ページのURL
URL = "https://www.pokemoncenter-online.com/lottery/apply.html"
# LINEのトークン
LINE_TOKEN = os.environ.get('LINE_TOKEN')

def send_line(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=data)

def check_lottery():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
    }
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        # 「公開中の抽選がありません」という文字があるかチェック
        if "公開中の抽選がありません" in response.text:
            # 何もない時もLINEを送るように変更しました
            send_line("【ポケセン定期確認】現在、受付中の抽選販売はありません。")
            print("「なし」の通知を送りました。")
        else:
            # 何かがある場合
            send_line(f"【ポケセン通知】★新しい抽選販売が開始された可能性があります！★\n確認してください：\n{URL}")
            print("抽選開始の可能性があるため、通知を送りました。")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # エラーが起きた時もLINEをくれるようにしておきます
        send_line(f"【ポケセン通知】エラーが発生しました。設定を確認してください。\n{e}")

if __name__ == "__main__":
    check_lottery()
