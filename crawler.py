import requests
import pandas as pd
from datetime import datetime
import os

# --- 🛠️ 基地設定區域 ---
# 國泰系列 (使用 API 模式)
CATHAY_TARGETS = {
    "00400A": "EA",
    "00981A": "I7",
    "00982A": "I8",
    "00992A": "I9"
}

# 復華系列 (使用 Excel 下載模式)
FUHUA_TARGETS = {
    "00991A": "ETF23"
}

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*, text/html",
    }

# --- 🌸 國泰採集邏輯 (JSON API) ---
def crawl_cathay(etf_name, fund_code):
    print(f"🚀 [國泰] 小蜜蜂出動：{etf_name}")
    api_url = f"https://cwapi.cathaysite.com.tw/api/ETF/GetETFDetailStockList?FundCode={fund_code}"
    try:
        response = requests.get(api_url, headers=get_headers(), timeout=15)
        json_data = response.json()
        stock_list = json_data.get('result', [])
        
        if stock_list:
            data = []
            for item in stock_list:
                data.append({
                    "股票代號": str(item.get("stockCode", "")).strip(),
                    "股票名稱": str(item.get("stockName", "")).strip(),
                    "持股股數_純數字": str(item.get("volumn", "")).replace(',', '').strip(),
                    "權重%": str(item.get("weights", "")).strip()
                })
            df = pd.DataFrame(data)
            today_str = datetime.now().strftime("%Y%m%d")
            filename = f"holdings_{etf_name}_{today_str}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ {etf_name} 採集成功！")
        else:
            print(f"⚠️ {etf_name} API 未回傳資料。")
    except Exception as e:
        print(f"❌ {etf_name} 發生錯誤：{e}")

# --- 🌸 復華採集邏輯 (Excel 直接對接) ---
def crawl_fuhua(etf_name, fund_id):
    print(f"🚀 [復華] 小蜜蜂出動：{etf_name}")
    today_str = datetime.now().strftime("%Y%m%d")
    # 復華的 Excel 下載路徑
    excel_url = f"https://www.fhtrust.com.tw/api/assetsExcel/{fund_id}/{today_str}"
    
    try:
        response = requests.get(excel_url, headers=get_headers(), timeout=20)
        if response.status_code == 200:
            filename = f"holdings_{etf_name}_{today_str}.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ {etf_name} Excel 下載成功！(已儲存為 {filename})")
        else:
            print(f"⚠️ {etf_name} 官網尚未更新今日 Excel。")
    except Exception as e:
        print(f"❌ {etf_name} 下載失敗：{e}")

# --- 🎬 執行區 ---
if __name__ == "__main__":
    print(f"✨ 啟動時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行國泰軍團
    for name, code in CATHAY_TARGETS.items():
        crawl_cathay(name, code)
        
    # 執行復華軍團
    for name, code in FUHUA_TARGETS.items():
        crawl_fuhua(name, code)
        
    print("🌸 所有採集任務已完成，小粉回基地休息囉！")