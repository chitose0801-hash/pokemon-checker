import requests
from bs4 import BeautifulSoup
import os

def check_pokemon():
    # 新着一覧ページ
    url = "https://www.pokemoncenter-online.com/?main_page=product_list&sort=new"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 商品リストの解析
        items = soup.select(".reco_item_inner") 
        message = ""

        for item in items:
            name_element = item.select_one(".name")
            if not name_element:
                continue
                
            name = name_element.text.strip()
            # 商品全体のテキストから「予約」や「抽選」を探す
            item_text = item.text
            
            if "予約" in item_text or "抽選" in item_text:
                message += f"\n【予約/抽選 開始】\n{name}\n"

        if message:
            send_line(f"ポケセン新着情報：{message}")
        else:
            print("予約・抽選商品は見つかりませんでした。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

def send_line(msg):
    token = os.environ.get("LINE_TOKEN")
    if not token:
        print("LINE_TOKENが設定されていません。")
        return
        
    api_url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(api_url, headers=headers, data={"message": msg})

if __name__ == "__main__":
    check_pokemon()
