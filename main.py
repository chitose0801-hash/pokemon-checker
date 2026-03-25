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
    requests.post(url, headers=headers, json=data)

def parse_miyagi_info(title, content):
    """宮城県の情報を探し、指定の箇条書きフォーマットに整える"""
    # 商品名はタイトルから取得
    product_name = title.replace("【予約情報】", "").strip()
    
    # 宮城県に関連する行を抽出
    # ブログの構造上、都道府県ごとにまとまっていることが多いため「宮城県」前後のテキストを探す
    lines = content.split('\n')
    miyagi_data = []
    is_miyagi_section = False
    
    for line in lines:
        if "宮城県" in line:
            miyagi_data.append(line)
    
    if not miyagi_data:
        return None # 宮城県の情報がなければ送信しない

    # メッセージ構築
    now = datetime.now().strftime("%m/%d %H:%M")
    msg = f"📍 宮城県 予約情報（{now}確認）\n"
    msg += f"━━━━━━━━━━━━━━━\n"
    
    for info in miyagi_data:
        # 店舗名を抽出（例：ホビーステーション仙台店）
        shop = "不明"
        shop_match = re.search(r"([^ 　]+(?:店|ショップ|センター))", info)
        if shop_match: shop = shop_match.group(1)
        
        # 受付期間
        start_date = "不明"
        end_date = "不明"
        date_matches = re.findall(r"(\d{1,2}/\d{1,2})", info)
        if len(date_matches) >= 2:
            start_date, end_date = date_matches[0], date_matches[1]
        elif len(date_matches) == 1:
            end_date = date_matches[0]
            
        # 応募方法
        method = "店頭" if "店頭" in info else "Web" if "Web" in info or "アプリ" in info else "不明"

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
        
        if not items: return

        # 最新3件の記事をチェック（宮城県の情報が含まれる記事を探すため）
        for item in items[:3]:
            title = item.title.text
            content = item.description.text
            link = item.link.text
            
            message = parse_miyagi_info(title, content)
            if message:
                message += f"🔗 詳細：{link}"
                send_line(message)
                print(f"宮城県の情報を送信しました: {title}")
                break # 1つ見つかったら終了

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_blog()
