import requests
import os

# 抽選ページのURL
URL = "https://www.pokemoncenter-online.com/lottery/apply.html"
LINE_TOKEN = os.environ.get('LINE_TOKEN')

def send_line(message):
    if not LINE_TOKEN:
        print("LINE_TOKENが設定されていません")
        return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

def check_lottery():
    # 403エラーを避けるため、ブラウザからのアクセスを装う
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://www.pokemoncenter-online.com/"
    }
    try:
        # タイムアウトを設定して接続
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        if "公開中の抽選がありません" in response.text:
            send_line("【ポケセン定期確認】現在、受付中の抽選販売はありません。")
            print("確認完了：抽選なし")
        else:
            send_line(f"【ポケセン通知】新しい抽選販売が開始された可能性があります！\n{URL}")
            print("確認完了：抽選あり！")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            msg = "ポケセン側から一時的にブロック（403）されました。しばらく時間を置いて再試行されます。"
            print(msg)
            # 頻繁に送るとうるさいので、エラー時はprintのみにするか必要ならLINE送る
        else:
            send_line(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    check_lottery()
