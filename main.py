import requests
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 設定
LINE_TOKEN = os.environ.get('LINE_TOKEN')
# RSSではなく、直接ブログのトップページを読み込む方式に切り替えて確実性を上げます
BLOG_URL = "https://pokecainfo.livedoor.blog/"

def send_line(message):
    if not LINE_TOKEN: return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

def parse_miyagi_info(title, html_content):
    now = datetime.now().strftime("%m/%d %H:%M")
    product_name = re.sub(r'【.*?】', '', title).strip()

    # HTMLタグを除去してテキストのみにする
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n')
    lines = text.split('\n')
    
    miyagi_lines = [l.strip() for l in lines if "宮城県" in l or "仙台" in l]
    
    if not miyagi_lines:
        return f"📢 {now} 確認\n宮城県の予約情報はありません。\n\n最新の記事:\n{title}"

    msg = f"📍 宮城県 予約情報（{now}）\n"
    msg += f"━━━━━━━━━━━━━━━\n"
    
    for info in miyagi_lines:
        # 店舗名の抽出
        shop = "不明"
        shop_match = re.search(r"(?:宮城県|仙台市)[：:\s]*(.*?)(?:\s|\d|/|（|$)", info)
        if shop_match: shop = shop_match.group(1).strip()
        
        # 日付の抽出
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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        # RSSではなく直接ページを読みに行く
        response = requests.get(BLOG_URL, headers=headers, timeout=15)
        response.encoding = 'euc-jp' # ライブドアブログの文字コード
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 最新の記事（一番上の記事）を見つける
        article = soup.find('article') or soup.find(class_='article-outer')
        if not article:
            send_line("ブログの構造が変わったため、記事を見つけられませんでした。")
            return

        title = article.find(class_='article-title').get_text().strip()
        link = article.find(class_='article-title').find('a').get('href')
        content = article.find(class_='article-body').get_text()

        message = parse_miyagi_info(title, content)
        if message:
            message += f"🔗 詳細：{link}"
            send_line(message)

    except Exception as e:
        print(f"Error: {e}")
        send_line(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    check_blog()
