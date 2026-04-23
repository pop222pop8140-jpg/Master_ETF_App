import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

print("🌸 呼叫小粉！00992A 專屬小蜜蜂準備出動！")

# 1. 鎖定目標網址 (群益 00992A 申購買回清單)
url = "https://www.capitalfund.com.tw/etf/product/detail/500/buyback"

# 偽裝成真人瀏覽器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

try:
    # 潛入群益官網取得網頁代碼
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    nav_value = 0.0

    # --- 🕵️‍♀️ 任務 A：抓取總淨資產 (NAV) ---
    nav_label = soup.find('div', string=re.compile('基金淨資產價值'))
    if nav_label:
        nav_td = nav_label.find_next_sibling('div', class_=re.compile('td'))
        if nav_td:
            # 清洗文字：把 "TWD"、逗號和空白清掉
            nav_text = nav_td.text.replace('TWD', '').replace(',', '').strip()
            nav_value = float(nav_text)
            print(f"💰 成功攔截總淨資產：{nav_value} 元")

    # --- 🕵️‍♀️ 任務 B：抓取股票清單 ---
    stock_tbody = soup.find('div', class_=re.compile('pct-stock-table-tbody'))
    if stock_tbody:
        # 尋找電腦版顯示的表格列
        rows = stock_tbody.find_all('div', class_=re.compile(r'tr\s+show-for-medium'))
        for row in rows:
            cols = row.find_all('div')
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

    # --- 🕵️‍♀️ 任務 C：抓取現金餘額 ---
    cash_label = soup.find('div', string=re.compile('現金'))
    if cash_label:
        cash_td = cash_label.find_next_sibling('div', class_=re.compile('td'))
        if cash_td:
            cash_text = cash_td.text.replace('TWD', '').replace(',', '').strip()
            data.append({
                "股票代號": "_CASH",
                "股票名稱": "現金",
                "持股股數_純數字": cash_text, # 現金類直接填金額，我們的主程式會自動轉換
                "權重%": "-",
                "__NAV_VALUE": nav_value
            })
            print(f"💵 成功攔截現金子彈：{cash_text} 元")

    # --- 💾 任務 D：寫入 CSV 並收工 ---
    if data:
        today_str = datetime.now().strftime("%Y%m%d")
        filename = f"holdings_00992A_{today_str}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 00992A 採集大成功！資料已平安送達 {filename} 🍯")
    else:
        print("⚠️ 哎呀！網頁裡面沒有找到資料，群益投信可能改版了！")

except Exception as e:
    print(f"❌ 小蜜蜂撞到牆了：{e}")