import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# 設定
RSS_URL = "https://pokecainfo.livedoor.blog/index.xml"
LINE_TOKEN = os.environ.get('LINE_TOKEN')

def send_line(message):
    if not LINE_TOKEN: return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    res = requests.post(url, headers=headers, json=data)
    print(f"LINE送信ステータス: {res.status_code}")

def parse_miyagi_info(title, content):
    now = datetime.now().strftime("%m/%d %H:%M")
    # タイトルから【】などを除去して商品名にする
    product_name = re.sub(r'【.*?】', '', title).strip()

    # 改行コードを統一して1行ずつチェック
    clean_content = content.replace('<br />', '\n').replace('<br>', '\n')
    lines = clean_content.split('\n')
    
    # 「宮城県」または「仙台」が含まれる行を抽出
    miyagi_lines = [l for l in lines if "宮城県" in l or "仙台" in l]
    
    # ★宮城県の情報がない場合のメッセージ
    if not miyagi_lines:
        return f"📢 {now} 確認\n宮城県の予約情報はありません。\n\n最新の記事:\n{title}"

    # 宮城県の情報がある場合のメッセージ構築
    msg = f"📍 宮城県 予約情報（{now}）\n"
    msg += f"━━━━━━━━━━━━━━━\n"
    
    for info in miyagi_lines:
        # 店舗名の抽出
        shop = "不明"
        shop_match = re.search(r"(?:宮城県|仙台市)[：:\s]*(.*?)(?:\s|\d|/)", info)
        if shop_match: shop = shop_match.group(1).strip()
        
        # 受付期間（日付 0/0 を探す）
        dates = re.findall(r"(\d{1,2}/\d{1,2})", info)
        start_date = dates[0] if len(dates) >= 1 else "不明"
        end_date = dates[1] if len(dates) >= 2 else "不明"
            
        # 応募方法
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
            print("記事が取得できませんでした")
            return

        # 最新の記事1件を対象にする
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
