import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

print("🌸 呼叫小粉！00400A (國泰動能高息) 專屬小蜜蜂準備出動！")

# 鎖定目標網址 (國泰 00400A 持股權重)
url = "https://www.cathaysite.com.tw/ETF/detail/EEA?tab=etf3"

# 偽裝成真人瀏覽器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

try:
    # 潛入國泰官網取得網頁代碼
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    nav_value = 0.0

    # --- 🕵️‍♀️ 任務 A：抓取最新預估淨值 ---
    nav_div = soup.find(lambda tag: tag.name == "div" and "每受益權單位淨資產價值" in tag.text)
    if nav_div:
        nav_td = nav_div.find_next_sibling('div')
        if nav_td:
            nav_text = nav_td.text.replace('TWD', '').replace(',', '').strip()
            nav_value = float(nav_text)
            print(f"💰 成功攔截最新淨值：{nav_value} 元")

    # --- 🕵️‍♀️ 任務 B：抓取股票清單 ---
    stock_tbody = soup.find('div', class_=lambda c: c and 'pct-stock-table-tbody' in c)
    if stock_tbody:
        # 國泰的表格列是用 tr show-for-medium 這些 class 組成的
        rows = stock_tbody.find_all('div', class_=lambda c: c and 'tr' in c and 'show-for-medium' in c)
        for row in rows:
            cols = row.find_all('div', recursive=False)
            if len(cols) >= 4:
                stock_code = cols[0].text.strip()
                stock_name = cols[1].text.strip()
                weight = cols[2].text.strip()
                shares = cols[3].text.replace(',', '').strip()

                data.append({
                    "股票代號": stock_code,
                    "股票名稱": stock_name,
                    "持股股數_純數字": shares,
                    "權重%": weight,
                    "__NAV_VALUE": nav_value
                })

    # --- 🕵️‍♀️ 任務 C：抓取現金與保證金 ---
    for tag in soup.find_all('div', class_=lambda c: c and 'th' in c):
        text = tag.text.strip()
        if text == '現金':
            td = tag.find_next_sibling('div')
            if td:
                val_text = td.text.replace('TWD', '').replace(',', '').strip()
                data.append({
                    "股票代號": "_CASH",
                    "股票名稱": "現金",
                    "持股股數_純數字": val_text,
                    "權重%": "-",
                    "__NAV_VALUE": nav_value
                })
                print(f"💵 成功攔截現金子彈：{val_text} 元")
        elif text == '保證金':
            td = tag.find_next_sibling('div')
            if td:
                val_text = td.text.replace('TWD', '').replace(',', '').strip()
                data.append({
                    "股票代號": "_GDM",
                    "股票名稱": "期貨保證金",
                    "持股股數_純數字": val_text,
                    "權重%": "-",
                    "__NAV_VALUE": nav_value
                })
                print(f"🛡️ 成功攔截保證金：{val_text} 元")

    # --- 💾 任務 D：寫入 CSV 並收工 ---
    if data:
        today_str = datetime.now().strftime("%Y%m%d")
        filename = f"holdings_00400A_{today_str}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 00400A 採集大成功！資料已平安送達 {filename} 🍯")
    else:
        print("⚠️ 找不到資料，國泰網頁結構可能改變了！")

except Exception as e:
    print(f"❌ 00400A 小蜜蜂撞到牆了：{e}")