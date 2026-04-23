import requests
import pandas as pd
import json
import html
import re
from datetime import datetime

URL = "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW"

def scrape_00981a_v19():
    print("🌸 小粉啟動『全資產穿透模式』！正在搜尋 00981A 所有金庫...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        match = re.search(r'id="DataAsset"\s+data-content="([^"]+)"', response.text)
        
        if not match: return print("❌ 找不到數據櫃...")
            
        data_list = json.loads(html.unescape(match.group(1)))
        holdings_list = []
        nav_value = 0
        data_date = ""

        # 1. 先找出總水位與正確日期
        for item in data_list:
            if item.get("AssetCode") == "NAV":
                nav_value = item.get("Value", 0)
                # 從 EditDate 或 EndDate 抓日期比較精準
                raw_date = item.get("EditDate", "")
                data_date = raw_date.split("T")[0].replace("-", "") if raw_date else datetime.now().strftime("%Y%m%d")

        # 2. 抓取所有資產項目 (包含股票、現金、保證金)
        for item in data_list:
            code = item.get("AssetCode")
            name = item.get("AssetName")
            val = item.get("Value", 0)
            weight = (val / nav_value * 100) if nav_value else 0

            # 📈 處理股票 (ST)
            if code == "ST" and "Details" in item:
                for d in item["Details"]:
                    holdings_list.append({
                        "股票代號": str(d.get("DetailCode", "")).strip(),
                        "股票名稱": d.get("DetailName", ""),
                        "持股股數_純數字": d.get("Share", 0),
                        "權重%": d.get("NavRate", 0),
                        "__NAV_VALUE": nav_value
                    })
            # 💰 處理現金、保證金、應收付帳款等「資本」
            elif code in ["CASH", "GDM", "APAR", "PAY"]:
                holdings_list.append({
                    "股票代號": f"_{code}", # 加上底線作為特殊標記
                    "股票名稱": f"💎 {name}",
                    "持股股數_純數字": val, # 資本直接放金額
                    "權重%": round(weight, 2),
                    "__NAV_VALUE": nav_value
                })

        df = pd.DataFrame(holdings_list)
        filename = f"holdings_00981A_{data_date}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"💰 基金水位：{nav_value:,.0f} 元")
        print(f"📅 交易日期：{data_date}")
        print(f"✅ 成功把股票與資本都裝進：{filename}")
        return filename

    except Exception as e:
        print(f"❌ 錯誤：{e}")

if __name__ == "__main__":
    scrape_00981a_v19()