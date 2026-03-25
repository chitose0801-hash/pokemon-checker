import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# 設定
RSS_URL = "https://meli-melo.blog.jp/archives/cat_1250027.xml"
LINE_TOKEN = os.environ.get('LINE_TOKEN')

def send_line(message):
    if not LINE_TOKEN: return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

def extract_info(title, content, link):
    """記事の内容から情報を抜き出し、不足分は「不明」とする"""
    now = datetime.now().strftime("%m/%d %H:%M")
    
    # 商品名
    name = title.replace("【予約】", "").replace("【抽選】", "").strip() if title else "不明"
    
    # 予約期間（日付のパターンをいくつか探す）
    period_match = re.search(r"(\d{1,2}/\d{1,2}.*?まで)", content)
    period = period_match.group(1) if period_match else "不明"
    
    # 予約場所（キーワードから推測）
    place = "不明"
    if "ポケモンセンター" in content or "ポケセン" in content:
        place = "ポケモンセンターオンライン"
    elif "Amazon" in content:
        place = "Amazon"
    elif "楽天" in content:
        place = "楽天市場"
    elif "ヨドバシ" in content:
        place = "ヨドバシカメラ"

    # 価格
    price_match = re.search(r"(\d{1,3}(?:,\d{3})*)円", content)
    price = f"{price_match.group(1)}円" if price_match else "不明"

    # 指定のフォーマット
    msg = f"{now}分の予約情報\n"
    msg += f"商品名:{name}\n"
    msg += f"予約期間:{period}\n"
    msg += f"予約場所:{place}\n"
    msg += f"価格:{price}\n"
    msg += f"URL:{link}"
    return msg

def check_blog():
    try:
        # User-Agentを設定してアクセスを安定させる
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        if not items:
            print("記事が見つかりませんでした")
            return

        # 最新の1件を取得
        latest_item = items[0]
        title = latest_item.title.text if latest_item.title else ""
        link = latest_item.link.text if latest_item.link else ""
        content = latest_item.description.text if latest_item.description else ""

        message = extract_info(title, content, link)
        send_line(message)
        print("送信完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    check_blog()
