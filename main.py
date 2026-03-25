import requests
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 設定（GitHubのSecretsに登録した名前）
LINE_TOKEN = os.environ.get('LINE_TOKEN')
RSS_URL = "https://pokecainfo.livedoor.blog/index.xml"

def send_line(message):
    if not LINE_TOKEN:
        print("エラー: LINE_TOKENが設定されていません")
        return
    
    # Messaging API用の設定
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {
        "messages": [{"type": "text", "text": message}]
    }
    
    res = requests.post(url, headers=headers, json=payload)
    print(f"ステータスコード: {res.status_code}")
    print(f"レスポンス: {res.text}")

def parse_miyagi_info(title, content):
    now = datetime.now().strftime("%m/%d %H:%M")
    product_name = re.sub(r'【.*?】', '', title).strip()

    clean_content = content.replace('<br />', '\n').replace('<br>', '\n')
    lines = clean_content.split('\n')
    
    miyagi_lines = [l for l in lines if "宮城県" in l or "仙台" in l]
    
    if not miyagi_lines:
        return f"📢 {now} 確認\n宮城県の予約情報はありません。\n\n最新の記事:\n{title}"

    msg = f"📍 宮城県 予約情報（{now}）\n"
    msg += f"━━━━━━━━━━━━━━━\n"
    
    for info in miyagi_lines:
        shop = "不明"
        shop_match = re.search(r"(?:宮城県|仙台市)[：:\s]*(.*?)(?:\s|\d|/)", info)
        if shop_match: shop = shop_match.group(1).strip()
        
        dates = re.findall(r"(\d{1,2}/\d{1,2})", info)
        start_date = dates[0] if len(dates) >= 1 else "不明"
        end_date = dates[1] if len(dates) >= 2 else "不明"
            
        method = "店頭" if "店頭" in info else "Web/アプリ" if any(k in info for k in ["Web", "アプリ", "抽選"]) else "不明"

        msg += f"■{product_name}\n"
        msg += f"　店舗名：{shop}\n"
        msg += f"　受付開始：{start_date}\n"
        msg += f"　受付終了：{end_date}\n"
        msg += f"　応募方法：{method}\n\n"
        
    return msg

def check_blog():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        if not items:
            send_line("ブログ記事が取得できませんでした。")
            return

        item = items[0]
        title = item.title.text
        content = item.description.text if item.description else ""
        link = item.link.text
        
        message = parse_miyagi_info(title, content)
        if message:
            message += f"🔗 詳細：{link}"
            send_line(message)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_blog()
