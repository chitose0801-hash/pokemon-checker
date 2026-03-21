import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.pokemoncenter-online.com/lottery/apply.html"
LINE_TOKEN = os.environ.get('LINE_TOKEN')

def send_line(message):
    if not LINE_TOKEN: return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

def check_lottery():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 抽選商品のリストを探す（ポケセンの画面構造に合わせる）
        lottery_items = soup.select(".lottery-item") # 実際の構造に合わせて解析
        
        if not lottery_items or "公開中の抽選がありません" in response.text:
            send_line("ポケモンセンターオンラインにて抽選予約は行われていません。")
            print("抽選なし")
        else:
            msg = "【ポケセン抽選開始！】\n\n"
            for item in lottery_items:
                name = item.select_one(".title").text.strip() if item.select_one(".title") else "不明な商品"
                price = item.select_one(".price").text.strip() if item.select_one(".price") else "価格不明"
                
                # ジャンル判別（商品名から推測）
                genre = "その他"
                if "カード" in name or "BOX" in name or "パック" in name:
                    genre = "ポケモンカード系"
                elif "ぬいぐるみ" in name:
                    genre = "ぬいぐるみ系"
                
                msg += f"■商品：{name}\n■ジャンル：{genre}\n■価格：{price}\n"
            
            msg += f"\n詳細はこちら：\n{URL}"
            send_line(msg)
            print("抽選あり：詳細を送信しました")
            
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    check_lottery()
