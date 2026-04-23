import requests
import pandas as pd
from datetime import datetime

print("🌸 呼叫小粉！00400A (國泰動能高息) API 專屬小蜜蜂準備出動！")

# 目標 API 網址
api_url = "https://cwapi.cathaysite.com.tw/api/ETF/GetETFDetailStockList?FundCode=EEA"

# 偽裝成真人瀏覽器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

try:
    # 潛入 API 金庫直接拿資料
    response = requests.get(api_url, headers=headers, timeout=15)
    response.raise_for_status()
    
    # 將回傳的文字轉換成 JSON 字典
    json_data = response.json()
    data = []

    # 根據主人的截圖，國泰的資料是放在 'result' 這個箱子裡面
    stock_list = json_data.get('result', [])

    # 開始解析股票清單
    if stock_list and isinstance(stock_list, list):
        for item in stock_list:
            # 🎯 精準對應國泰的特殊標籤名稱 (注意大小寫與 volumn 拼字)
            stock_code = str(item.get("stockCode", "")).strip()
            stock_name = str(item.get("stockName", "")).strip()
            weight = str(item.get("weights", "")).strip()
            # 國泰的股數帶有逗號，順手把它清除變成純數字
            shares = str(item.get("volumn", "")).replace(',', '').strip()

            if stock_code:  # 確保有抓到股票代號
                data.append({
                    "股票代號": stock_code,
                    "股票名稱": stock_name,
                    "持股股數_純數字": shares,
                    "權重%": weight,
                    "__NAV_VALUE": 0.0  # API 沒有給淨值，先填 0
                })

    # --- 💾 寫入 CSV 並收工 ---
    if data:
        today_str = datetime.now().strftime("%Y%m%d")
        filename = f"holdings_00400A_{today_str}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 00400A API 採集大成功！資料已平安送達 {filename} 🍯")
    else:
        print("⚠️ 金庫裡沒有找到資料，請檢查 API 結構！")

except Exception as e:
    print(f"❌ 00400A 小蜜蜂撞到牆了：{e}")